import json

import pytest
from sqlalchemy import func, select

from creative_os.config import repo_root
from creative_os.importers.handoff import import_handoff
from creative_os.models import (
    Account,
    ConceptBatch,
    ConceptCandidate,
    Creative,
    ManualEvaluation,
    ModelRun,
    Program,
    StoryAuditRecord,
    StoryLockVersion,
)
from creative_os.providers.reasoning import (
    ALLOWED_OUTPUTS,
    DISABLED_CAPABILITIES,
    CreativeReasoningProvider,
    GrokReasoningProvider,
    ReasoningResult,
)
from creative_os.schemas.story_lock import StoryLockDocument
from creative_os.services.baseline import apply_preservation_baseline
from creative_os.services.concepts import ConceptError, decide_concept
from creative_os.services.context_bundles import create_context_bundle
from creative_os.services.context_compiler import compile_context
from creative_os.services.diversity import audit_batch, fingerprint_concept
from creative_os.services.evaluations import ORIGIN, import_manual_evaluations
from creative_os.services.identity import USAGE_GUIDANCE, assess_account_identity, identity_anchors
from creative_os.services.product_identity import (
    clear_target_identifier_if_present,
    product_identifier_findings,
)
from creative_os.services.tasks import create_creative_task
from creative_os.services.text_reasoning import (
    ReasoningBoundaryError,
    assert_capability_disabled,
    compare_providers,
    execute_text_reasoning,
    run_count,
)
from creative_os.services.validate_creative import validate_creative
from creative_os.util import utcnow

pytestmark = pytest.mark.core

_SUPERSEDED = "superseded: Apple AirPods 4 Wireless Earbuds, TCIN 85978615"
_AUDIT = {
    "overall_status": "READY",
    "diagnosis": "The locked story holds.",
    "hook_assessment": "kept",
    "propulsion_assessment": "kept",
    "viral_texture_assessment": "kept",
    "continuity_assessment": "kept",
    "comment_door_assessment": "kept",
    "commerce_integration_assessment": "kept",
    "proof_boundary_assessment": "kept",
    "recommended_changes": ["Clear the stale identifier if a human agrees."],
    "recommended_patches": [{"path": "/floating_hook", "value": "rewritten by the model"}],
    "things_to_preserve": ["hook"],
    "uncertainties": [],
}


class ScriptedProvider(CreativeReasoningProvider):
    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self._text = text

    def available(self) -> bool:
        return True

    def generate_concepts(self, packet_text: str) -> ReasoningResult:
        self.seen = packet_text
        return ReasoningResult(text=self._text, model_name=self.name)

    def audit_story_development(self, packet_text: str) -> ReasoningResult:
        self.seen = packet_text
        return ReasoningResult(text=self._text, model_name=self.name)


def _rows(concepts: list[dict]) -> list[dict]:
    return [
        {"title": concept["title"], "mechanism_fingerprint": fingerprint_concept(concept)}
        for concept in concepts
    ]


def _concept(title: str, premise: str) -> dict:
    return {"title": title, "premise": premise, "family": "I"}


def _import(session) -> Creative:
    import_handoff(session, repo_root() / "source_snapshots/2026-10-05")
    session.flush()
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    assert creative is not None
    return creative


def _maria_bundle(session, constraints: dict | None = None):
    creative = _import(session)
    program = session.get(Program, creative.program_id)
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    assert program is not None and maria is not None
    task = create_creative_task(
        session,
        program_id=program.id,
        account_id=maria.id,
        ecosystem_id=creative.ecosystem_id,
        stage="CONCEPT_GENERATION",
        instruction="Propose concepts for Maria.",
        created_by="operator",
        constraints=constraints or {},
    )
    bundle = create_context_bundle(session, None, task=task, as_of=utcnow())
    return maria, bundle


def test_three_shared_skeletons_are_low() -> None:
    payload = json.loads(
        (repo_root() / "evaluation/model_transfer_v1/runs/grok_maria_concepts.json").read_text()
    )
    report = audit_batch(_rows(payload["concepts"]))
    assert report["level"] == "LOW"
    flagged = report["flagged_repeated_skeletons"]
    assert flagged
    cluster = next(item for item in flagged if item["skeleton"] == "claim_versus_commerce_proof")
    assert cluster["count"] >= 3
    assert "the plain bag was on purpose" not in cluster["titles"]
    assert "everyone was gonna bring their own" not in cluster["titles"]
    repair = report["repair_plan"]
    assert repair["generates_replacements"] is False
    assert repair["keep"]
    assert len(repair["replace_for_diversity"]) >= 2
    assert "mishap_consequence" in repair["underrepresented"]
    assert "gift_surprise" in repair["underrepresented"]


def test_distinct_skeletons_are_not_low() -> None:
    concepts = [
        _concept("edited after the order went in", "The placed order is the proof."),
        _concept("sad bag", "Teammates misread the bag and called it shorted."),
        _concept("hidden gift", "A birthday surprise gift stays hidden."),
        _concept("overslept", "A mishap started when she overslept and spilled coffee."),
        _concept("bring their own", "Everyone was gonna bring their own for the hosted night."),
    ]
    report = audit_batch(_rows(concepts))
    assert report["level"] == "HIGH"
    assert report["repair_plan"] is None
    social = fingerprint_concept(concepts[1])
    assert "proof_mechanism" not in social
    assert social["primary_attention_engine"]["assignment"] == "model_extracted"


def test_variant_request_allows_a_repeated_skeleton() -> None:
    concepts = [
        _concept("edited after the order went in", "The order is the proof."),
        _concept("he said he was the one who ordered", "The receipt order contradicts the claim."),
        _concept("mom thinks she cooked", "The order proof contradicts what she thinks she did."),
    ]
    open_report = audit_batch(_rows(concepts))
    assert open_report["level"] == "LOW"
    allowed = audit_batch(_rows(concepts), {"requested_variants_of": "claim_versus_commerce_proof"})
    assert allowed["level"] != "LOW"
    assert "variants" in allowed["reason"]
    broad = audit_batch(_rows(concepts), {"allow_repeated_skeleton": True})
    assert broad["level"] != "LOW"


def test_identity_wording_is_not_a_contradiction() -> None:
    anchors = identity_anchors(
        [
            {
                "field_name": "recurring_relationship",
                "value": "Dre as boyfriend",
                "evidence_kind": "HUMAN_SET_CONSTRAINT",
                "confidence": "HUMAN_SET",
            }
        ]
    )
    assert anchors[0]["canonical_name"] == "Dre"
    assert anchors[0]["relationship_type"] == "boyfriend"
    assert anchors[0]["status"] == "ESTABLISHED"
    assert anchors[0]["usage_guidance"] == USAGE_GUIDANCE
    generic = assess_account_identity("my boyfriend picked up the order", anchors)
    assert generic["level"] == "GENERIC_WORDING"
    assert generic["contradiction"] is False
    named = assess_account_identity("boyfriend named Marcus picked it up", anchors)
    assert named["contradiction"] is True
    husband = assess_account_identity("my husband picked it up", anchors)
    assert husband["level"] == "WRONG_ACCOUNT_REALITY"
    specific = assess_account_identity("Dre picked it up", anchors)
    assert specific["level"] == "ACCOUNT_SPECIFIC"
    assert specific["contradiction"] is False


def test_unknown_identifier_stays_valid_and_superseded_identifier_fails() -> None:
    current = StoryLockDocument(
        title="AirPods",
        line_items=[{"position": 3, "title": "Apple AirPods 5 Wireless Earbuds", "model": "AirPods 5"}],
    )
    unknown = current.model_copy(deep=True)
    unknown.line_items[0].external_id = "11111111"
    assert product_identifier_findings(unknown, "no identifier clause") == []
    stale = current.model_copy(deep=True)
    stale.line_items[0].external_id = "85978615"
    findings = product_identifier_findings(stale, _SUPERSEDED)
    assert findings[0]["status"] == "FAIL"
    assert findings[0]["known_owner"] == "Apple AirPods 4 Wireless Earbuds"


def test_manual_evaluations_do_not_create_model_runs(session) -> None:
    assert run_count(session) == 0
    inserted = import_manual_evaluations(session)
    assert inserted == 4
    assert import_manual_evaluations(session) == 0
    rows = session.scalars(select(ManualEvaluation)).all()
    assert {row.origin for row in rows} == {ORIGIN}
    assert {row.rubric_score for row in rows} == {"26/26", "17/18"}
    assert all(row.packet_hash and row.output_json and row.rubric_item_scores for row in rows)
    assert run_count(session) == 0


def test_airpods_identifier_is_cleared_without_a_replacement(session) -> None:
    creative = _import(session)
    apply_preservation_baseline(session)
    version = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    assert version is not None and version.version_number == 1
    before = {name: status for name, status, _message in validate_creative(session, creative)}
    assert before["product_identifier:85978615"] == "FAIL"
    cleared = clear_target_identifier_if_present(session)
    assert cleared not in {"missing", "already_clear"}
    current = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    assert current is not None and current.version_number == 2
    document = StoryLockDocument.model_validate(current.content_json)
    airpods = next(item for item in document.line_items if "AirPods 5" in item.title)
    assert airpods.external_id is None
    assert all(item.external_id != "85978615" for item in document.line_items)
    historical = session.get(StoryLockVersion, version.id)
    assert historical is not None
    old = StoryLockDocument.model_validate(historical.content_json)
    assert any(item.external_id == "85978615" for item in old.line_items)
    after = {name: status for name, status, _message in validate_creative(session, creative)}
    assert after["product_identifier"] == "PASS"
    package = compile_context(session, creative, stage="STORY_DEVELOPMENT")
    assert package["genome_state"] == "GENOME_PENDING_FOR_CURRENT_LOCK"
    assert package["provider_execution"] == "NOT_IMPLEMENTED"


def test_maria_packet_exposes_dre_without_the_holdout_rubric(session) -> None:
    _maria, bundle = _maria_bundle(session)
    anchors = bundle.compiled_payload["account_dna"]["identity_anchors"]
    assert anchors[0]["canonical_name"] == "Dre"
    assert anchors[0]["relationship_type"] == "boyfriend"
    assert anchors[0]["usage_guidance"] == USAGE_GUIDANCE
    text = bundle.compiled_text
    assert "canonical_name Dre" in text
    assert USAGE_GUIDANCE in text
    assert "human-approved account context" in text
    assert "This rubric is for the human reviewer only" not in text
    assert bundle.compiled_payload["provider_execution"] == "NOT_IMPLEMENTED"
    assert bundle.compiler_version == "context-compiler-0.3.1"


def test_text_reasoning_stays_inside_its_boundary(session, monkeypatch) -> None:
    maria, bundle = _maria_bundle(session)
    dna_pointer = maria.current_approved_dna_profile_id
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    assert creative is not None
    lock_pointer = creative.current_approved_story_lock_version_id
    hook = StoryLockDocument.model_validate(
        session.get(StoryLockVersion, lock_pointer).content_json
    ).floating_hook
    payload = {
        "concepts": [
            _concept("my boyfriend left", "my boyfriend sent the food"),
            _concept("boyfriend named Marcus", "boyfriend named Marcus sent the food"),
            _concept("edited after the order went in", "The order is the proof of the claim."),
            _concept("edited after the order went in again", "The order proof repeats the claim."),
            _concept("edited after another order", "The order proof repeats the claim again."),
        ]
    }
    provider = ScriptedProvider("scripted", json.dumps(payload))
    other = ScriptedProvider("other", json.dumps(payload))
    runs = compare_providers(session, bundle, [provider, other])
    assert provider.seen == other.seen == bundle.compiled_text
    assert {run.context_bundle_id for run in runs} == {bundle.id}
    assert {run.context_bundle_hash for run in runs} == {bundle.payload_hash}
    assert all(run.input_tokens is None and run.output_tokens is None for run in runs)
    assert all(run.cached_tokens is None and run.cost is None and run.cost_currency is None for run in runs)
    concepts = session.scalars(
        select(ConceptCandidate).where(ConceptCandidate.task_id == bundle.creative_task_id)
    ).all()
    assert concepts
    assert {concept.status for concept in concepts} == {"PROPOSED"}
    generic = next(row for row in concepts if row.title == "my boyfriend left")
    assert generic.structured_payload["account_identity"]["contradiction"] is False
    invented = next(row for row in concepts if "Marcus" in row.title)
    assert invented.structured_payload["account_identity"]["contradiction"] is True
    batch = session.scalars(select(ConceptBatch)).first()
    assert batch is not None and batch.diversity_level == "LOW"
    with pytest.raises(ConceptError):
        decide_concept(session, concepts[0], "SELECT", actor=concepts[0].created_by)
    decide_concept(session, concepts[0], "SELECT", actor="operator")
    assert concepts[0].status == "SELECTED"
    assert maria.current_approved_dna_profile_id == dna_pointer
    assert creative.current_approved_story_lock_version_id == lock_pointer

    program = session.get(Program, creative.program_id)
    assert program is not None
    audit_task = create_creative_task(
        session,
        program_id=program.id,
        account_id=creative.account_id,
        creative_id=creative.id,
        campaign_id=creative.campaign_id,
        ecosystem_id=creative.ecosystem_id,
        stage="STORY_DEVELOPMENT",
        instruction="Audit the current story.",
        created_by="operator",
    )
    audit_bundle = create_context_bundle(session, creative, task=audit_task, as_of=utcnow())
    versions = session.scalar(select(func.count()).select_from(StoryLockVersion))
    audit_run = execute_text_reasoning(session, audit_bundle, ScriptedProvider("scripted", json.dumps(_AUDIT)))
    assert audit_run.status == "COMPLETED"
    assert audit_run.context_bundle_hash == audit_bundle.payload_hash
    record = session.scalar(select(StoryAuditRecord).where(StoryAuditRecord.model_run_id == audit_run.id))
    assert record is not None and record.record_status == "MODEL_DIAGNOSIS"
    assert creative.current_approved_story_lock_version_id == lock_pointer
    assert session.scalar(select(func.count()).select_from(StoryLockVersion)) == versions
    current = StoryLockDocument.model_validate(session.get(StoryLockVersion, lock_pointer).content_json)
    assert current.floating_hook == hook

    broken = execute_text_reasoning(session, bundle, ScriptedProvider("scripted", "this is not json"))
    assert broken.status == "PARSE_FAILED"
    assert broken.raw_response == "this is not json"
    assert broken.parsed_output is None
    fenced = "note\n```json\n{broken\n```"
    child = execute_text_reasoning(session, bundle, ScriptedProvider("scripted", fenced))
    assert child.status == "PARSE_FAILED"
    assert child.parent_run_id is not None
    parent = session.get(ModelRun, child.parent_run_id)
    assert parent is not None and parent.raw_response == fenced

    for name in ("web_research", "image_generation", "posting", "pinterest", "visual_search"):
        assert name in DISABLED_CAPABILITIES
        with pytest.raises(ReasoningBoundaryError):
            assert_capability_disabled(name)
    assert ALLOWED_OUTPUTS == {"CONCEPT_GENERATION", "STORY_DEVELOPMENT_AUDIT"}
    research = create_creative_task(
        session,
        program_id=program.id,
        account_id=creative.account_id,
        creative_id=creative.id,
        campaign_id=creative.campaign_id,
        ecosystem_id=creative.ecosystem_id,
        stage="RESEARCH",
        instruction="Research the web.",
        created_by="operator",
    )
    research_bundle = create_context_bundle(session, creative, task=research, as_of=utcnow())
    before_runs = run_count(session)
    with pytest.raises(ReasoningBoundaryError):
        execute_text_reasoning(session, research_bundle, ScriptedProvider("scripted", "{}"))
    assert run_count(session) == before_runs

    monkeypatch.delenv("COS_XAI_API_KEY", raising=False)
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    missing = execute_text_reasoning(session, bundle, GrokReasoningProvider())
    assert missing.status == "NOT_IMPLEMENTED"
    assert missing.execution_origin == "LIVE_TEXT_REASONING"
    assert missing.context_bundle_hash == bundle.payload_hash
