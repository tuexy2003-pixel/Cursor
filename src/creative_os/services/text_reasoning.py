"""Run a frozen context bundle through a text reasoning provider. The provider only reads and returns."""

import json
import re
from datetime import datetime
from typing import Any

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from creative_os.models import (
    ConceptBatch,
    ContextBundle,
    Creative,
    ModelProvider,
    ModelRun,
    StoryAuditRecord,
)
from creative_os.providers.reasoning import (
    ALLOWED_OUTPUTS,
    DISABLED_CAPABILITIES,
    MAX_PROVIDERS_PER_COMPARISON,
    CreativeReasoningProvider,
    ProviderHTTPError,
    ProviderModelMismatch,
    ProviderTimeout,
    ProviderUnavailable,
    ReasoningResult,
)
from creative_os.schemas.contracts import ConceptGenerationResult, StoryDevelopmentAuditResult
from creative_os.services.concepts import propose_concept
from creative_os.services.diversity import audit_batch, fingerprint_concept
from creative_os.services.execution_gate import (
    authorization_block,
    claim_invocation,
    finish_authorization,
    mark_requesting,
)
from creative_os.services.identity import assess_account_identity
from creative_os.util import utcnow

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


class ReasoningBoundaryError(ValueError):
    pass


def execute_text_reasoning(
    session: Session,
    bundle: ContextBundle,
    provider: CreativeReasoningProvider,
    *,
    parent_run_id: str | None = None,
    allow_repair: bool = True,
    authorization: Any = None,
    idempotency_key: str | None = None,
) -> ModelRun:
    output_name = _output_name(bundle)
    if output_name not in ALLOWED_OUTPUTS:
        raise ReasoningBoundaryError(f"text reasoning is only enabled for {', '.join(sorted(ALLOWED_OUTPUTS))}")
    if provider.uses_paid_transport:
        return _execute_paid(
            session,
            bundle,
            provider,
            output_name,
            authorization=authorization,
            idempotency_key=idempotency_key,
            allow_repair=allow_repair,
        )
    started = utcnow()
    if not provider.available():
        return _store_run(
            session,
            bundle,
            provider,
            started=started,
            finished=utcnow(),
            status="NOT_IMPLEMENTED",
            error="provider execution is not enabled",
            parent_run_id=parent_run_id,
        )
    try:
        result = _call(provider, bundle.compiled_text, output_name)
    except ProviderUnavailable as exc:
        return _store_run(
            session,
            bundle,
            provider,
            started=started,
            finished=utcnow(),
            status="NOT_IMPLEMENTED",
            error=str(exc),
            parent_run_id=parent_run_id,
        )
    except Exception as exc:
        return _store_run(
            session,
            bundle,
            provider,
            started=started,
            finished=utcnow(),
            status="PROVIDER_ERROR",
            error=str(exc),
            parent_run_id=parent_run_id,
        )
    parsed, error = _parse(result.text, output_name)
    run = _store_run(
        session,
        bundle,
        provider,
        started=started,
        finished=utcnow(),
        status="COMPLETED" if parsed is not None else "PARSE_FAILED",
        raw_response=result.text,
        parsed=parsed,
        parse_error=error,
        result=result,
        parent_run_id=parent_run_id,
        error=error,
    )
    if parsed is None:
        if allow_repair and _fenced_json(result.text) is not None:
            return execute_text_reasoning(
                session,
                bundle,
                _RepairProvider(provider, _fenced_json(result.text) or ""),
                parent_run_id=run.id,
                allow_repair=False,
            )
        return run
    if output_name == "CONCEPT_GENERATION":
        _store_concepts(session, bundle, run, ConceptGenerationResult.model_validate(parsed))
    else:
        _store_audit(session, bundle, run, StoryDevelopmentAuditResult.model_validate(parsed))
    return run


def compare_providers(
    session: Session,
    bundle: ContextBundle,
    providers: list[CreativeReasoningProvider],
    *,
    authorization: Any = None,
    idempotency_prefix: str | None = None,
) -> list[ModelRun]:
    if len(providers) > MAX_PROVIDERS_PER_COMPARISON:
        raise ReasoningBoundaryError("this phase allows at most 2 providers")
    runs: list[ModelRun] = []
    for provider in providers:
        key = None if idempotency_prefix is None else f"{idempotency_prefix}:{provider.name}"
        runs.append(
            execute_text_reasoning(
                session,
                bundle,
                provider,
                authorization=authorization,
                idempotency_key=key,
            )
        )
    return runs


def assert_capability_disabled(capability: str) -> None:
    if capability in DISABLED_CAPABILITIES:
        raise ReasoningBoundaryError(f"{capability} execution is disabled")
    if capability not in {"concept_generation", "story_development_audit", "creative_reasoning"}:
        raise ReasoningBoundaryError(f"{capability} is not a text-reasoning stage")


class _RepairProvider(CreativeReasoningProvider):
    """RESPONSE SALVAGE of the same provider text. This is not a second network call."""

    def __init__(self, parent: CreativeReasoningProvider, text: str) -> None:
        self.name = parent.name
        self._text = text
        self._parent = parent

    def available(self) -> bool:
        return True

    def generate_concepts(self, packet_text: str) -> ReasoningResult:
        return ReasoningResult(text=self._text, model_name=self.name, model_version="response-salvage")

    def audit_story_development(self, packet_text: str) -> ReasoningResult:
        return ReasoningResult(text=self._text, model_name=self.name, model_version="response-salvage")


def authorize_and_run_once(
    session: Session,
    bundle: ContextBundle,
    provider: CreativeReasoningProvider,
    *,
    actor: str,
    idempotency_key: str,
) -> ModelRun:
    from creative_os.config import get_settings
    from creative_os.services.execution_gate import (
        AuthorizationError,
        create_authorization,
        find_invocation,
        preflight,
    )

    if actor != get_settings().operator_identity:
        raise AuthorizationError("only the local operator can authorize a paid run")
    if not idempotency_key.strip():
        raise AuthorizationError("an idempotency key is required")
    existing = find_invocation(session, idempotency_key)
    if existing is not None and existing.model_run_id is not None:
        found = session.get(ModelRun, existing.model_run_id)
        if found is not None:
            return found
    view = preflight(session, bundle, provider)
    if view["execution_status"] != "READY":
        return _store_run(
            session,
            bundle,
            provider,
            started=utcnow(),
            finished=utcnow(),
            status=str(view["execution_status"]),
            error=str(view["execution_status"]),
            execution_state=str(view["execution_status"]),
        )
    authorization = create_authorization(
        session,
        bundle,
        provider,
        actor=actor,
        idempotency_key=idempotency_key,
        notes="single authorized text-reasoning attempt",
    )
    return execute_text_reasoning(
        session,
        bundle,
        provider,
        authorization=authorization,
        idempotency_key=idempotency_key,
    )


def _execute_paid(
    session: Session,
    bundle: ContextBundle,
    provider: CreativeReasoningProvider,
    output_name: str,
    *,
    authorization: Any,
    idempotency_key: str | None,
    allow_repair: bool,
) -> ModelRun:
    started = utcnow()
    readiness = provider.readiness()
    if readiness != "READY":
        return _blocked(session, bundle, provider, started, readiness, authorization)
    block = authorization_block(session, authorization, bundle, provider, output_name)
    if block is not None:
        return _blocked(session, bundle, provider, started, block, authorization)
    if not idempotency_key:
        return _blocked(session, bundle, provider, started, "AUTHORIZATION_REQUIRED", authorization)
    invocation, existing_run, created = claim_invocation(
        session, authorization, provider, bundle, idempotency_key
    )
    if not created:
        if existing_run is not None:
            return existing_run
        if invocation is not None:
            invocation.status = "UNKNOWN_PROVIDER_OUTCOME"
            invocation.error = "idempotent replay did not make another provider request"
            session.flush()
        return _blocked(session, bundle, provider, started, "UNKNOWN_PROVIDER_OUTCOME", authorization)
    if invocation is None:
        return _blocked(session, bundle, provider, started, "AUTHORIZATION_REQUIRED", authorization)
    provider.max_output_tokens = authorization.max_output_tokens
    mark_requesting(session, invocation, authorization)
    try:
        result = _call(provider, bundle.compiled_text, output_name)
    except ProviderTimeout as exc:
        return _paid_terminal(
            session, bundle, provider, invocation, authorization, started, "UNKNOWN_PROVIDER_OUTCOME", str(exc)
        )
    except ProviderHTTPError as exc:
        return _paid_terminal(
            session,
            bundle,
            provider,
            invocation,
            authorization,
            started,
            "PROVIDER_ERROR",
            str(exc),
            raw_response=exc.body,
        )
    except ProviderModelMismatch as exc:
        return _paid_terminal(
            session, bundle, provider, invocation, authorization, started, "PROVIDER_ERROR", str(exc)
        )
    except Exception as exc:
        return _paid_terminal(
            session,
            bundle,
            provider,
            invocation,
            authorization,
            started,
            "UNKNOWN_PROVIDER_OUTCOME",
            str(exc),
        )
    parsed, error = _parse(result.text, output_name)
    status = "COMPLETED" if parsed is not None else "PARSE_FAILED"
    run = _store_run(
        session,
        bundle,
        provider,
        started=started,
        finished=utcnow(),
        status=status,
        raw_response=result.text,
        parsed=parsed,
        parse_error=error,
        result=result,
        error=error,
        authorization_id=authorization.id,
        execution_state=status,
    )
    invocation.model_run_id = run.id
    invocation.provider_request_id = result.provider_request_id
    invocation.status = "PARSE_FAILED" if parsed is None else "COMPLETED"
    invocation.finished_at = utcnow()
    invocation.error = error
    finish_authorization(session, authorization)
    session.flush()
    if parsed is None:
        if allow_repair and _fenced_json(result.text) is not None:
            return execute_text_reasoning(
                session,
                bundle,
                _RepairProvider(provider, _fenced_json(result.text) or ""),
                parent_run_id=run.id,
                allow_repair=False,
            )
        return run
    if output_name == "CONCEPT_GENERATION":
        _store_concepts(session, bundle, run, ConceptGenerationResult.model_validate(parsed))
    else:
        _store_audit(session, bundle, run, StoryDevelopmentAuditResult.model_validate(parsed))
    return run


def _blocked(
    session: Session,
    bundle: ContextBundle,
    provider: CreativeReasoningProvider,
    started: datetime,
    status: str,
    authorization: Any,
) -> ModelRun:
    return _store_run(
        session,
        bundle,
        provider,
        started=started,
        finished=utcnow(),
        status=status,
        error=status,
        authorization_id=None if authorization is None else authorization.id,
        execution_state=status,
    )


def _paid_terminal(
    session: Session,
    bundle: ContextBundle,
    provider: CreativeReasoningProvider,
    invocation: Any,
    authorization: Any,
    started: datetime,
    status: str,
    error: str,
    raw_response: str | None = None,
) -> ModelRun:
    run = _store_run(
        session,
        bundle,
        provider,
        started=started,
        finished=utcnow(),
        status=status,
        error=error,
        raw_response=raw_response,
        authorization_id=authorization.id,
        execution_state=status,
    )
    invocation.model_run_id = run.id
    invocation.status = status
    invocation.finished_at = utcnow()
    invocation.error = error
    finish_authorization(session, authorization)
    session.flush()
    return run


def _call(provider: CreativeReasoningProvider, packet_text: str, output_name: str) -> ReasoningResult:
    if output_name == "CONCEPT_GENERATION":
        return provider.generate_concepts(packet_text)
    return provider.audit_story_development(packet_text)


def _output_name(bundle: ContextBundle) -> str:
    payload = bundle.compiled_payload or {}
    task = payload.get("task") or {}
    name = task.get("expected_output_type")
    if name:
        return str(name)
    stage = str(payload.get("requested_stage") or bundle.requested_stage)
    if stage == "CONCEPT_GENERATION":
        return "CONCEPT_GENERATION"
    if stage == "STORY_DEVELOPMENT":
        return "STORY_DEVELOPMENT_AUDIT"
    return stage


def _parse(text: str, output_name: str) -> tuple[dict[str, Any] | None, str | None]:
    candidate = text.strip()
    fenced = _fenced_json(candidate)
    if candidate.startswith("{") or candidate.startswith("["):
        body = candidate
    elif fenced and (fenced.startswith("{") or fenced.startswith("[")):
        body = fenced
    else:
        return None, "provider response is not a JSON object"
    try:
        loaded = json.loads(body)
    except json.JSONDecodeError as exc:
        return None, f"provider response is not valid JSON: {exc.msg}"
    model = ConceptGenerationResult if output_name == "CONCEPT_GENERATION" else StoryDevelopmentAuditResult
    try:
        return model.model_validate(loaded).model_dump(mode="json"), None
    except ValidationError as exc:
        return None, f"provider response failed the output contract: {exc.errors()[0]['msg']}"


def _fenced_json(text: str) -> str | None:
    match = _FENCE.search(text)
    if match is None:
        return None
    return match.group(1).strip()


def _store_concepts(
    session: Session,
    bundle: ContextBundle,
    run: ModelRun,
    result: ConceptGenerationResult,
) -> None:
    from creative_os.models import CreativeTask

    task = session.get(CreativeTask, bundle.creative_task_id) if bundle.creative_task_id else None
    if task is None:
        raise ReasoningBoundaryError("concept generation requires the bundle's creative task")
    batch = ConceptBatch(
        task_id=task.id,
        source_model_run_id=run.id,
        created_at=utcnow(),
        status="PROPOSED",
        diversity_report={},
    )
    session.add(batch)
    session.flush()
    anchors = ((bundle.compiled_payload or {}).get("account_dna") or {}).get("identity_anchors") or []
    rows: list[dict[str, Any]] = []
    concept_ids: list[str] = []
    for draft in result.concepts:
        payload = draft.model_dump(mode="json")
        fingerprint = fingerprint_concept(payload)
        identity_text = " ".join(
            str(payload.get(key) or "") for key in ("title", "premise", "human_event", "why_it_fits_account")
        )
        payload["account_identity"] = assess_account_identity(identity_text, anchors)
        payload["mechanism_fingerprint"] = fingerprint
        concept = propose_concept(
            session,
            task=task,
            title=draft.title,
            created_by=run.provider_model_name or "provider",
            premise=draft.premise,
            family=draft.family,
            hook_direction=draft.hook_direction,
            commerce_relation=(draft.commerce_relation or "")[:80] or None,
            structured_payload=payload,
            source_model_run_id=run.id,
            batch_id=batch.id,
            mechanism_fingerprint=fingerprint,
        )
        concept_ids.append(concept.id)
        rows.append({"id": concept.id, "title": concept.title, "mechanism_fingerprint": fingerprint})
    constraints = task.constraints if isinstance(task.constraints, dict) else {}
    report = audit_batch(rows, constraints)
    batch.diversity_level = report["level"]
    batch.diversity_report = report
    run.output_refs = {
        "concept_batch_id": batch.id,
        "concept_ids": concept_ids,
        "diversity_level": report["level"],
    }
    session.flush()


def _store_audit(
    session: Session,
    bundle: ContextBundle,
    run: ModelRun,
    result: StoryDevelopmentAuditResult,
) -> None:
    creative_id = bundle.creative_id
    before = None
    if creative_id:
        creative = session.get(Creative, creative_id)
        before = None if creative is None else creative.current_approved_story_lock_version_id
    record = StoryAuditRecord(
        model_run_id=run.id,
        context_bundle_id=bundle.id,
        creative_id=creative_id,
        overall_status=result.overall_status,
        diagnosis=result.diagnosis,
        result_json=result.model_dump(mode="json"),
        record_status="MODEL_DIAGNOSIS",
        created_at=utcnow(),
    )
    session.add(record)
    session.flush()
    run.output_refs = {"story_audit_record_id": record.id, "record_status": "MODEL_DIAGNOSIS"}
    if creative_id:
        creative = session.get(Creative, creative_id)
        after = None if creative is None else creative.current_approved_story_lock_version_id
        if after != before:
            raise ReasoningBoundaryError("a story audit must not move the approved story lock")


def _store_run(
    session: Session,
    bundle: ContextBundle,
    provider: CreativeReasoningProvider,
    *,
    started: datetime,
    finished: datetime,
    status: str,
    error: str | None = None,
    raw_response: str | None = None,
    parsed: dict[str, Any] | None = None,
    parse_error: str | None = None,
    result: ReasoningResult | None = None,
    parent_run_id: str | None = None,
    authorization_id: str | None = None,
    provider_request_id: str | None = None,
    execution_state: str | None = None,
) -> ModelRun:
    provider_row = session.scalar(
        select(ModelProvider).where(
            ModelProvider.name == provider.name,
            ModelProvider.capability == "creative_reasoning",
        )
    )
    latency = int((finished - started).total_seconds() * 1000)
    model_name = provider.name
    if result is not None and result.model_name:
        model_name = result.model_name
    run = ModelRun(
        provider_id=None if provider_row is None else provider_row.id,
        capability="creative_reasoning",
        status=status,
        started_at=started,
        finished_at=finished,
        input_refs={"context_bundle_id": bundle.id, "context_bundle_hash": bundle.payload_hash},
        output_refs={},
        cost=None if result is None else result.cost,
        latency_ms=max(latency, 0),
        error=error,
        context_bundle_id=bundle.id,
        creative_task_id=bundle.creative_task_id,
        context_bundle_hash=bundle.payload_hash,
        provider_model_name=model_name,
        provider_model_version=None if result is None else result.model_version,
        raw_response=raw_response,
        parsed_output=parsed,
        parse_error=parse_error,
        parent_run_id=parent_run_id,
        input_tokens=None if result is None else result.input_tokens,
        output_tokens=None if result is None else result.output_tokens,
        cached_tokens=None if result is None else result.cached_tokens,
        cost_currency=None if result is None else result.currency,
        usage_metadata=None if result is None else result.usage,
        execution_origin="LIVE_TEXT_REASONING",
        run_authorization_id=authorization_id,
        provider_request_id=provider_request_id if result is None else result.provider_request_id,
        execution_state=execution_state or status,
    )
    session.add(run)
    session.flush()
    return run


def run_count(session: Session) -> int:
    return int(session.scalar(select(func.count()).select_from(ModelRun)) or 0)
