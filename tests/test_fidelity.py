from datetime import timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.config import repo_root
from creative_os.importers.handoff import import_handoff
from creative_os.models import (
    Account,
    AccountDnaObservation,
    ApprovalEvent,
    Creative,
    Ecosystem,
    GenomeFacet,
    PolicyRule,
    Program,
)
from creative_os.models.entities import ImmutableVersionError
from creative_os.services.concepts import ConceptError, decide_concept, link_selected_concept, propose_concept
from creative_os.services.context_bundles import create_context_bundle
from creative_os.services.context_compiler import compile_context
from creative_os.services.lifecycle import mark_lifecycle
from creative_os.services.model_transfer import MARIA_INSTRUCTION, TARGET_INSTRUCTION, build_transfer_bundles
from creative_os.services.scope import ScopeError
from creative_os.services.story_locks import apply_story_lock_correction
from creative_os.services.tasks import create_creative_task
from creative_os.util import utcnow

pytestmark = pytest.mark.core

STORY_PHRASES = (
    "my birthday is literally today 😭",
    "grabbing stuff for the house rn",
    "bc you're nosy 😭",
    "ok now i'm looking",
    "AirPods 5",
    "$19.23",
)


def _creative(session) -> Creative:
    import_handoff(session, repo_root() / "source_snapshots/2026-10-05")
    session.flush()
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    assert creative is not None
    return creative


def _task(session, creative: Creative, stage: str = "STORY_DEVELOPMENT", **kwargs):
    return create_creative_task(
        session,
        program_id=kwargs.get("program_id", creative.program_id),
        account_id=kwargs.get("account_id", creative.account_id),
        campaign_id=kwargs.get("campaign_id", creative.campaign_id),
        creative_id=kwargs.get("creative_id", creative.id),
        ecosystem_id=kwargs.get("ecosystem_id", creative.ecosystem_id),
        stage=stage,
        instruction=kwargs.get("instruction", "Audit the current story."),
        created_by="operator",
        constraints=kwargs.get("constraints"),
        expected_output_type=kwargs.get("expected_output_type"),
    )


def test_story_lock_survives_without_the_creative_policy_note(session) -> None:
    creative = _creative(session)
    note = session.scalar(select(PolicyRule).where(PolicyRule.code == "principles-d-creative-lock-note"))
    assert note is not None
    mark_lifecycle(note)
    note.status = "superseded"
    session.flush()
    moment = utcnow()
    task = _task(session, creative)
    bundle = create_context_bundle(session, creative, task=task, as_of=moment, heuristic_budget=0)
    text = bundle.compiled_text
    for phrase in STORY_PHRASES:
        assert phrase in text
    document = bundle.compiled_payload["current_story_lock_version"]["document"]
    assert len(document["line_items"]) == 5
    assert document["comment_doors"]
    assert document["continuity"]
    assert document["viral_texture"]
    locks = bundle.compiled_payload["creative_locks"]
    assert all(item["code"] != "principles-d-creative-lock-note" for item in locks)
    assert "principles-d-creative-lock-note" not in text


def test_budget_zero_keeps_authoritative_context(session) -> None:
    creative = _creative(session)
    moment = utcnow()
    task = _task(session, creative, instruction="Keep the lock and the invariants.")
    package = compile_context(
        session, creative, heuristic_budget=0, as_of=moment, include_skill_content=True, task=task
    )
    assert package["global_invariants"]
    assert all(item["rule_kind"] == "INVARIANT" for item in package["global_invariants"])
    assert any(item["rule_kind"] == "LOCKED_VALUE" for item in package["creative_locks"])
    assert package["task"]["instruction"] == "Keep the lock and the invariants."
    assert package["current_story_lock_version"]["document"]["floating_hook"] == (
        "my birthday is literally today 😭"
    )
    skills = {item["slug"]: item for item in package["skill_versions"]}
    assert "story-development" in skills
    assert len(skills["story-development"]["content"]) > 80
    excluded = {item.get("code") for item in package["excluded_for_token_budget"]}
    kept = {item["code"] for item in package["global_invariants"] + package["creative_locks"]}
    assert excluded.isdisjoint(kept)


def test_optional_policy_prefers_the_specific_scope(session) -> None:
    creative = _creative(session)
    moment = utcnow()
    session.add_all(
        [
            PolicyRule(
                code="aaa-early",
                scope_level="GLOBAL",
                scope_id=None,
                rule_kind="HEURISTIC",
                title="early global heuristic",
                text="global optional",
                status="active",
                content_hash="aaa-early-hash",
                approval_state="APPROVED",
                effective_from=moment - timedelta(days=1),
                created_at=moment,
            ),
            PolicyRule(
                code="zzz-local",
                scope_level="CREATIVE",
                scope_id=creative.id,
                rule_kind="PREFERENCE",
                title="later creative preference",
                text="local optional",
                status="active",
                content_hash="zzz-local-hash",
                approval_state="APPROVED",
                effective_from=moment - timedelta(days=1),
                created_at=moment,
            ),
        ]
    )
    session.flush()
    task = _task(session, creative)
    package = compile_context(session, creative, heuristic_budget=1, as_of=moment, task=task)
    optional_codes = [
        item["code"]
        for item in package["global_invariants"]
        + package["program_policies"]
        + package["account_policies"]
        + package["campaign_policies"]
        + package["creative_locks"]
        if item["code"] in {"aaa-early", "zzz-local"}
    ]
    assert optional_codes == ["zzz-local"]
    excluded = {item.get("code") for item in package["excluded_for_token_budget"]}
    assert "aaa-early" in excluded
    local = next(item for item in package["creative_locks"] if item["code"] == "zzz-local")
    assert local["priority"].startswith("scope=0")


def test_stage_skill_map(session) -> None:
    creative = _creative(session)
    moment = utcnow()
    research = _slugs(session, creative, "RESEARCH", moment)
    assert research == {
        "story-conflict-scout",
        "object-culture-scout",
        "live-heat-scout",
        "source-card",
        "commerce-world-mapper",
    }
    assert "adaptation-blitz-match" not in research
    assert "find-purchase-screens-on-pinterest" not in research
    concept = _slugs(session, creative, "CONCEPT_GENERATION", moment)
    assert concept == {
        "synthetic-story-generator",
        "commercial-aware-synthesis",
        "adaptation-blitz-match",
    }
    story = _slugs(session, creative, "STORY_DEVELOPMENT", moment)
    assert story == {"story-development"}
    routing = _slugs(session, creative, "PRODUCTION_ROUTING", moment)
    assert routing == {
        "production-spec-qa",
        "visual-surface-acquisition",
        "find-purchase-screens-on-pinterest",
    }
    specialist = create_creative_task(
        session,
        program_id=creative.program_id,
        creative_id=creative.id,
        ecosystem_id=creative.ecosystem_id,
        campaign_id=creative.campaign_id,
        stage="STORY_DEVELOPMENT",
        instruction="Use the chat specialist.",
        created_by="operator",
        constraints={"specialist_skills": ["chat-story-slideshow"]},
    )
    chat = compile_context(session, creative, as_of=moment, task=specialist)
    assert "chat-story-slideshow" in {item["slug"] for item in chat["skill_versions"]}
    qa = _slugs(session, creative, "PRODUCTION_QA", moment)
    assert qa == {"production-spec-qa", "ios-26-production-normalization"}
    performance = compile_context(session, creative, stage="PERFORMANCE_INTERPRETATION", as_of=moment)
    assert performance["skill_coverage"] == "MISSING_DEDICATED_SKILL"
    assert performance["skill_versions"] == []


def test_concept_task_compiles_without_a_creative(session) -> None:
    creative = _creative(session)
    program = session.get(Program, creative.program_id)
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    doordash = session.scalar(select(Ecosystem).where(Ecosystem.code == "DOORDASH"))
    assert program is not None and maria is not None and doordash is not None
    moment = utcnow()
    task = create_creative_task(
        session,
        program_id=program.id,
        account_id=maria.id,
        ecosystem_id=doordash.id,
        stage="CONCEPT_GENERATION",
        instruction=MARIA_INSTRUCTION,
        created_by="operator",
    )
    bundle = create_context_bundle(session, None, task=task, as_of=moment)
    assert bundle.creative_id is None
    assert bundle.compiled_payload["current_story_lock_version"] is None
    slugs = {item["slug"] for item in bundle.compiled_payload["skill_versions"]}
    assert "getting-started" not in slugs
    assert "synthetic-story-generator" in slugs
    names = {item["name"] for item in bundle.compiled_payload["benchmarks"]}
    assert "SHE SAID IT WAS CHORE STUFF" not in names
    kinds = {row["evidence_kind"] for row in bundle.compiled_payload["account_dna"]["observations"]}
    assert "HUMAN_SET_CONSTRAINT" in kinds
    assert "HISTORICAL_OBSERVATION" in kinds
    assert all(row["source_path"] for row in bundle.compiled_payload["account_dna"]["observations"])
    assert "food and couples" in bundle.compiled_text
    with pytest.raises(ScopeError):
        create_creative_task(
            session,
            program_id=program.id,
            account_id=maria.id,
            campaign_id="missing-campaign",
            stage="RESEARCH",
            instruction="bad scope",
            created_by="operator",
        )


def test_genome_evidence_and_version_immutability(session) -> None:
    creative = _creative(session)
    moment = utcnow()
    task = _task(session, creative)
    package = compile_context(session, creative, as_of=moment, task=task)
    facets = package["creative_genome"]["facets"]
    assert facets
    assert all("assignment" in facet and "source" in facet and "confidence" in facet for facet in facets)
    facet = session.scalars(select(GenomeFacet)).first()
    assert facet is not None
    nested = session.begin_nested()
    facet.value = "changed"
    with pytest.raises(ImmutableVersionError):
        session.flush()
    nested.rollback()
    observation = session.scalars(select(AccountDnaObservation)).first()
    assert observation is not None
    nested = session.begin_nested()
    observation.value = "changed"
    with pytest.raises(ImmutableVersionError):
        session.flush()
    nested.rollback()


def test_task_is_immutable_after_a_bundle(session) -> None:
    creative = _creative(session)
    task = _task(session, creative)
    create_context_bundle(session, creative, task=task, as_of=utcnow())
    assert task.status == "CONSUMED"
    nested = session.begin_nested()
    task.instruction = "silent edit"
    with pytest.raises(ImmutableVersionError):
        session.flush()
    nested.rollback()


def test_human_selects_a_concept_and_story_context_keeps_it(session) -> None:
    creative = _creative(session)
    task = _task(session, creative, stage="CONCEPT_GENERATION", instruction="Propose a concept.")
    concept = propose_concept(
        session, task=task, title="Birthday cover", created_by="grok", premise="A sister lies."
    )
    assert concept.status == "PROPOSED"
    with pytest.raises(ConceptError):
        decide_concept(session, concept, "SELECT", actor="grok")
    decide_concept(session, concept, "SELECT", actor="operator", notes="human", creative=creative)
    assert concept.status == "SELECTED"
    assert creative.selected_concept_id == concept.id
    event = session.scalar(
        select(ApprovalEvent).where(
            ApprovalEvent.object_type == "concept_candidate",
            ApprovalEvent.object_id == concept.id,
            ApprovalEvent.status == "SELECTED",
        )
    )
    assert event is not None and event.actor == "operator"
    other = propose_concept(session, task=task, title="Other", created_by="grok")
    decide_concept(session, other, "SELECT", actor="operator")
    with pytest.raises(ConceptError):
        link_selected_concept(creative, other)
    story = _task(session, creative, instruction=TARGET_INSTRUCTION)
    package = compile_context(session, creative, as_of=utcnow(), task=story)
    assert package["selected_concept"]["title"] == "Birthday cover"


def test_packet_hash_tracks_authoritative_context(session) -> None:
    creative = _creative(session)
    moment = utcnow()
    task = _task(session, creative)
    first = create_context_bundle(session, creative, task=task, as_of=moment)
    second = create_context_bundle(session, creative, task=task, as_of=moment)
    assert first.payload_hash == second.payload_hash
    assert "STORY LOCK DOCUMENT" in first.compiled_text
    assert first.compiled_payload["section_sizes"]["story_lock"]["characters"] > 100
    apply_story_lock_correction(
        session, creative, {"floating_hook": "different hook"}, actor="operator", reason="new truth"
    )
    changed = create_context_bundle(session, creative, task=task, as_of=moment)
    assert changed.payload_hash != first.payload_hash
    assert changed.compiled_payload["genome_state"] == "GENOME_PENDING_FOR_CURRENT_LOCK"


def test_production_context_keeps_unknown_rights(session) -> None:
    creative = _creative(session)
    moment = utcnow()
    routing = _task(session, creative, stage="PRODUCTION_ROUTING", instruction="Route production.")
    package = compile_context(session, creative, as_of=moment, task=routing)
    assert package["assets"]
    assert any(asset["rights_status"] == "UNKNOWN" for asset in package["assets"])
    assert all("bytes" not in asset for asset in package["assets"])
    story = compile_context(session, creative, stage="STORY_DEVELOPMENT", as_of=moment)
    assert story["assets"] == []
    assert story["references"] == []


def test_transfer_packets_split_holdout_from_subject(session) -> None:
    _creative(session)
    story, concepts = build_transfer_bundles(session, utcnow())
    assert "my birthday is literally today 😭" in story.compiled_text
    assert story.compiled_payload["current_story_lock_version"]["document"]["economics"]["total"] == "19.23"
    assert concepts.creative_id is None
    assert concepts.compiled_payload["current_story_lock_version"] is None
    concept_names = {item["name"] for item in concepts.compiled_payload["benchmarks"]}
    assert "SHE SAID IT WAS CHORE STUFF" not in concept_names
    assert "my birthday is literally today 😭" not in concepts.compiled_text
    assert "SHE SAID IT WAS CHORE STUFF" not in concepts.compiled_text
    assert "THE ONIONS NOTE WAS BLANK" not in concepts.compiled_text
    assert concepts.compiled_payload["scope"]["account"]["slug"] == "maria"
    assert concepts.compiled_payload["scope"]["ecosystem"]["code"] == "DOORDASH"
    assert story.compiled_payload["scope"]["creative"]["holdout"] is True
    assert story.compiled_payload["scope"]["account"] is None
    rubric = "This rubric is for the human reviewer only."
    assert rubric not in story.compiled_text
    assert rubric not in concepts.compiled_text


def _slugs(session: Session, creative: Creative, stage: str, moment) -> set[str]:
    task = _task(session, creative, stage=stage, instruction=f"Run {stage}.")
    package = compile_context(session, creative, as_of=moment, task=task)
    return {item["slug"] for item in package["skill_versions"]}
