"""Paid text reasoning stays behind the live flag, a human authorization, and one attempt."""

import json
from email.message import Message
from io import BytesIO
from urllib.error import HTTPError

import pytest
from sqlalchemy import func, select

from creative_os.config import get_settings, repo_root
from creative_os.importers.handoff import import_handoff
from creative_os.models import (
    Account,
    ConceptCandidate,
    ContextBundle,
    Creative,
    CreativeTask,
    ModelRun,
    PolicyRule,
    Program,
    RunAuthorization,
    StoryAuditRecord,
    StoryLockVersion,
)
from creative_os.providers.reasoning import (
    DISABLED_CAPABILITIES,
    GrokReasoningProvider,
    OpenAIReasoningProvider,
)
from creative_os.services.context_bundles import create_context_bundle
from creative_os.services.diversity import audit_batch, fingerprint_concept
from creative_os.services.execution_gate import AuthorizationError, create_authorization
from creative_os.services.identity import assess_account_identity
from creative_os.services.smoke import prepare_smoke_tests
from creative_os.services.tasks import create_creative_task
from creative_os.services.text_reasoning import (
    ReasoningBoundaryError,
    authorize_and_run_once,
    compare_providers,
    execute_text_reasoning,
)
from creative_os.util import utcnow

pytestmark = pytest.mark.core

_CONCEPTS = {
    "concepts": [
        {"title": "overslept the drop", "premise": "A mishap started when she overslept."},
        {"title": "hidden birthday", "premise": "A birthday surprise gift stays hidden."},
    ]
}
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
    "recommended_changes": [],
    "recommended_patches": [],
    "things_to_preserve": ["hook"],
    "uncertainties": [],
}


class _Body:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def read(self) -> bytes:
        return self.payload

    def __enter__(self) -> "_Body":
        return self

    def __exit__(self, *_args: object) -> bool:
        return False


def _bundle(session) -> ContextBundle:
    import_handoff(session, repo_root() / "source_snapshots/2026-10-05")
    session.flush()
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    program = session.get(Program, creative.program_id)
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    task = create_creative_task(
        session,
        program_id=program.id,
        account_id=maria.id,
        ecosystem_id=creative.ecosystem_id,
        stage="CONCEPT_GENERATION",
        instruction="Propose exactly 2 concepts.",
        created_by="operator",
        constraints={"concept_count": 2},
    )
    return create_context_bundle(session, None, task=task, as_of=utcnow())


def _other_bundle(session, creative: Creative) -> ContextBundle:
    program = session.get(Program, creative.program_id)
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    task = create_creative_task(
        session,
        program_id=program.id,
        account_id=maria.id,
        ecosystem_id=creative.ecosystem_id,
        stage="CONCEPT_GENERATION",
        instruction="A different frozen task.",
        created_by="operator",
    )
    return create_context_bundle(session, None, task=task, as_of=utcnow())


def _enable(monkeypatch, *, model: str = "explicit-test-model", limit: str = "10") -> None:
    monkeypatch.setenv("COS_XAI_API_KEY", "test-key-not-a-real-secret")
    monkeypatch.setenv("COS_XAI_MODEL", model)
    monkeypatch.setenv("COS_LIVE_TEXT_REASONING_ENABLED", "true")
    monkeypatch.setenv("COS_TEXT_REASONING_DAILY_RUN_LIMIT", limit)
    get_settings()


def _chat(payload: dict, *, model: str = "explicit-test-model", request_id: str | None = "resp_123") -> dict:
    body = {
        "id": request_id,
        "model": model,
        "choices": [{"message": {"content": json.dumps(payload)}}],
        "usage": {"prompt_tokens": 12, "completion_tokens": 4, "prompt_tokens_details": {"cached_tokens": 1}},
    }
    return body


def _patch(monkeypatch, responder) -> list[int]:
    calls: list[int] = []

    def urlopen(_req, timeout=90):
        calls.append(timeout)
        return responder()

    monkeypatch.setattr("creative_os.providers.reasoning.request.urlopen", urlopen)
    return calls


def _auths(session) -> int:
    return int(session.scalar(select(func.count()).select_from(RunAuthorization)) or 0)


def test_key_without_the_live_flag_makes_no_request(session, monkeypatch) -> None:
    bundle = _bundle(session)
    monkeypatch.setenv("COS_XAI_API_KEY", "test-key-not-a-real-secret")
    monkeypatch.setenv("COS_XAI_MODEL", "explicit-test-model")
    monkeypatch.setenv("COS_LIVE_TEXT_REASONING_ENABLED", "false")
    calls = _patch(monkeypatch, lambda: _Body(b"{}"))
    run = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="flag-off"
    )
    assert calls == []
    assert run.status == "EXECUTION_DISABLED"
    assert _auths(session) == 0
    assert "purchasing" in DISABLED_CAPABILITIES


def test_live_flag_without_authorization_makes_no_request(session, monkeypatch) -> None:
    bundle = _bundle(session)
    _enable(monkeypatch)
    calls = _patch(monkeypatch, lambda: _Body(b"{}"))
    run = execute_text_reasoning(session, bundle, GrokReasoningProvider())
    assert calls == []
    assert run.status == "AUTHORIZATION_REQUIRED"
    assert _auths(session) == 0


def test_authorization_rejects_a_different_bundle_and_provider(session, monkeypatch) -> None:
    bundle = _bundle(session)
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    other = _other_bundle(session, creative)
    _enable(monkeypatch)
    monkeypatch.setenv("COS_OPENAI_API_KEY", "test-key-not-a-real-secret")
    monkeypatch.setenv("COS_OPENAI_MODEL", "explicit-openai-model")
    calls = _patch(monkeypatch, lambda: _Body(b"{}"))
    with pytest.raises(AuthorizationError):
        create_authorization(
            session, bundle, GrokReasoningProvider(), actor="grok", idempotency_key="not-human"
        )
    authorization = create_authorization(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="human-auth"
    )
    mismatch = execute_text_reasoning(
        session,
        other,
        GrokReasoningProvider(),
        authorization=authorization,
        idempotency_key="other-bundle",
    )
    wrong_provider = execute_text_reasoning(
        session,
        bundle,
        OpenAIReasoningProvider(),
        authorization=authorization,
        idempotency_key="other-provider",
    )
    assert calls == []
    assert mismatch.status == "AUTHORIZATION_MISMATCH"
    assert wrong_provider.status == "AUTHORIZATION_MISMATCH"
    assert authorization.model_name == "explicit-test-model"
    assert authorization.context_bundle_hash == bundle.payload_hash


def test_the_same_idempotency_key_calls_the_provider_once(session, monkeypatch) -> None:
    bundle = _bundle(session)
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    dna = maria.current_approved_dna_profile_id
    policies = int(session.scalar(select(func.count()).select_from(PolicyRule)) or 0)
    _enable(monkeypatch)
    calls = _patch(monkeypatch, lambda: _Body(json.dumps(_chat(_CONCEPTS)).encode()))
    first = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="once"
    )
    second = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="once"
    )
    assert len(calls) == 1
    assert first.id == second.id
    assert first.status == "COMPLETED"
    assert first.provider_model_name == "explicit-test-model"
    assert first.provider_request_id == "resp_123"
    assert first.cost is None
    assert first.input_tokens == 12
    concepts = session.scalars(
        select(ConceptCandidate).where(ConceptCandidate.task_id == bundle.creative_task_id)
    ).all()
    assert len(concepts) == 2
    assert {row.status for row in concepts} == {"PROPOSED"}
    assert maria.current_approved_dna_profile_id == dna
    assert int(session.scalar(select(func.count()).select_from(PolicyRule)) or 0) == policies
    assert _auths(session) == 1


def test_timeout_is_unknown_and_is_not_retried(session, monkeypatch) -> None:
    bundle = _bundle(session)
    _enable(monkeypatch)
    calls = _patch(monkeypatch, lambda: (_ for _ in ()).throw(TimeoutError("timed out")))

    def urlopen(_req, timeout=90):
        calls.append(timeout)
        raise TimeoutError("timed out")

    monkeypatch.setattr("creative_os.providers.reasoning.request.urlopen", urlopen)
    first = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="timeout"
    )
    second = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="timeout"
    )
    assert calls == [90]
    assert first.id == second.id
    assert first.status == "UNKNOWN_PROVIDER_OUTCOME"
    assert session.scalar(select(func.count()).select_from(ConceptCandidate)) == 0


def test_http_error_and_malformed_body_do_not_retry(session, monkeypatch) -> None:
    bundle = _bundle(session)
    _enable(monkeypatch)

    def http_error(_req, timeout=90):
        http_error.calls += 1
        raise HTTPError(
            "https://api.x.ai/v1/chat/completions",
            500,
            "bad",
            Message(),
            BytesIO(b'{"error":"bad"}'),
        )

    http_error.calls = 0
    monkeypatch.setattr("creative_os.providers.reasoning.request.urlopen", http_error)
    failed = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="http"
    )
    again = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="http"
    )
    assert http_error.calls == 1
    assert failed.id == again.id
    assert failed.status == "PROVIDER_ERROR"

    def malformed(_req, timeout=90):
        malformed.calls += 1
        return _Body(b"not-json")

    malformed.calls = 0
    monkeypatch.setattr("creative_os.providers.reasoning.request.urlopen", malformed)
    broken = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="malformed"
    )
    authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="malformed"
    )
    assert malformed.calls == 1
    assert broken.status == "PROVIDER_ERROR"
    assert broken.raw_response == "not-json"
    assert session.scalar(select(func.count()).select_from(ConceptCandidate)) == 0


def test_daily_limit_blocks_the_next_attempt(session, monkeypatch) -> None:
    bundle = _bundle(session)
    _enable(monkeypatch, limit="1")
    calls = _patch(monkeypatch, lambda: _Body(json.dumps(_chat(_CONCEPTS)).encode()))
    authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="limit-a"
    )
    blocked = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="limit-b"
    )
    assert len(calls) == 1
    assert blocked.status == "DAILY_LIMIT_REACHED"


def test_missing_explicit_model_fails_before_a_call(session, monkeypatch) -> None:
    bundle = _bundle(session)
    monkeypatch.setenv("COS_XAI_API_KEY", "test-key-not-a-real-secret")
    monkeypatch.delenv("COS_XAI_MODEL", raising=False)
    monkeypatch.setenv("COS_LIVE_TEXT_REASONING_ENABLED", "true")
    calls = _patch(monkeypatch, lambda: _Body(b"{}"))
    run = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="no-model"
    )
    assert calls == []
    assert run.status == "NOT_CONFIGURED"
    assert _auths(session) == 0
    assert GrokReasoningProvider().readiness() == "NOT_CONFIGURED"


def test_invalid_output_and_fenced_salvage_make_one_call(session, monkeypatch) -> None:
    bundle = _bundle(session)
    _enable(monkeypatch)
    invalid = _chat({})
    invalid["choices"][0]["message"]["content"] = "this is not json"
    calls = _patch(monkeypatch, lambda: _Body(json.dumps(invalid).encode()))
    failed = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="bad-json"
    )
    assert len(calls) == 1
    assert failed.status == "PARSE_FAILED"
    assert failed.raw_response == "this is not json"
    assert session.scalar(select(func.count()).select_from(ConceptCandidate)) == 0

    fenced = _chat({})
    fenced["choices"][0]["message"]["content"] = "note\n```json\n" + json.dumps(_CONCEPTS) + "\n```"
    calls = _patch(monkeypatch, lambda: _Body(json.dumps(fenced).encode()))
    salvaged = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="fence"
    )
    assert len(calls) == 1
    assert salvaged.status == "COMPLETED"
    assert salvaged.parent_run_id is None
    assert session.scalar(select(func.count()).select_from(ConceptCandidate)) == 2


def test_story_audit_stays_a_diagnosis(session, monkeypatch) -> None:
    import_handoff(session, repo_root() / "source_snapshots/2026-10-05")
    session.flush()
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    pointer = creative.current_approved_story_lock_version_id
    program = session.get(Program, creative.program_id)
    task = create_creative_task(
        session,
        program_id=program.id,
        account_id=creative.account_id,
        creative_id=creative.id,
        campaign_id=creative.campaign_id,
        ecosystem_id=creative.ecosystem_id,
        stage="STORY_DEVELOPMENT",
        instruction="Diagnose only.",
        created_by="operator",
    )
    bundle = create_context_bundle(session, creative, task=task, as_of=utcnow())
    _enable(monkeypatch)
    calls = _patch(monkeypatch, lambda: _Body(json.dumps(_chat(_AUDIT, request_id=None)).encode()))
    run = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="audit-once"
    )
    record = session.scalar(select(StoryAuditRecord).where(StoryAuditRecord.model_run_id == run.id))
    assert len(calls) == 1
    assert run.status == "COMPLETED"
    assert run.provider_request_id is None
    assert record is not None and record.record_status == "MODEL_DIAGNOSIS"
    assert creative.current_approved_story_lock_version_id == pointer
    assert session.get(StoryLockVersion, pointer) is not None


def test_context_ceiling_blocks_before_a_call(session, monkeypatch) -> None:
    bundle = _bundle(session)
    _enable(monkeypatch)
    monkeypatch.setenv("COS_TEXT_REASONING_MAX_INPUT_TOKENS", "1")
    calls = _patch(monkeypatch, lambda: _Body(b"{}"))
    run = authorize_and_run_once(
        session, bundle, GrokReasoningProvider(), actor="operator", idempotency_key="too-big"
    )
    assert calls == []
    assert run.status == "CONTEXT_TOO_LARGE"
    assert _auths(session) == 0


def test_more_than_two_providers_are_rejected(session, monkeypatch) -> None:
    bundle = _bundle(session)

    class Scripted:
        name = "scripted"
        uses_paid_transport = False

        def readiness(self) -> str:
            return "NOT_IMPLEMENTED"

        def available(self) -> bool:
            return True

        def explicit_model(self) -> str | None:
            return None

        def generate_concepts(self, packet_text: str):
            raise AssertionError("comparison over the cap must not call a provider")

        def audit_story_development(self, packet_text: str):
            raise AssertionError("comparison over the cap must not call a provider")

    providers = [Scripted(), Scripted(), Scripted()]
    providers[1].name = "second"
    providers[2].name = "third"
    with pytest.raises(ReasoningBoundaryError):
        compare_providers(session, bundle, providers)
    _enable(monkeypatch)
    with pytest.raises(AuthorizationError):
        create_authorization(
            session,
            bundle,
            GrokReasoningProvider(),
            actor="operator",
            idempotency_key="too-many",
            allowed_providers=["grok", "openai", "other"],
            max_providers=3,
        )


def test_diversity_provenance_is_deterministic(session) -> None:
    import_handoff(session, repo_root() / "source_snapshots/2026-10-05")
    session.flush()
    social = fingerprint_concept(
        {"title": "sad bag", "premise": "Teammates misread the bag and called it shorted."}
    )
    assert social["primary_attention_engine"]["assignment"] == "DETERMINISTIC_INFERRED"
    assert social["primary_attention_engine"]["assignment"] != "model_extracted"
    report = audit_batch(
        [
            {"title": "unknown one", "mechanism_fingerprint": {}},
            {"title": "unknown two", "mechanism_fingerprint": {}},
            {
                "title": "overslept",
                "mechanism_fingerprint": fingerprint_concept(
                    {"title": "overslept", "premise": "she overslept"}
                ),
            },
        ]
    )
    assert report["level"] == "MEDIUM"
    assert report["assessment_method"] == "DETERMINISTIC_HEURISTIC"
    assert report["coverage"] == {"known_count": 1, "total_count": 3}
    identity = assess_account_identity(
        "my boyfriend sent it",
        [{"canonical_name": "Dre", "relationship_type": "boyfriend"}],
    )
    assert identity["advisory"] is True
    assert identity["method"] == "DETERMINISTIC_HEURISTIC"
    assert identity["contradiction"] is False
    prepare = prepare_smoke_tests(session)
    assert prepare["executed"] is False
    concept = prepare["concept_generation"]
    assert concept["constraints"]["concept_count"] == 2
    assert concept["stage"] == "CONCEPT_GENERATION"
    task = session.get(CreativeTask, concept["task_id"])
    assert task is not None and "Maria" in task.instruction
    again = prepare_smoke_tests(session)
    assert again["concept_generation"]["context_bundle_id"] == concept["context_bundle_id"]
    assert session.scalar(select(func.count()).select_from(ModelRun)) == 0
    assert _auths(session) == 0
    audit = prepare["story_development_audit"]
    assert audit["stage"] == "STORY_DEVELOPMENT_AUDIT"
    assert audit["executed"] is False
