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
    CreativeReasoningProvider,
    ProviderUnavailable,
    ReasoningResult,
)
from creative_os.schemas.contracts import ConceptGenerationResult, StoryDevelopmentAuditResult
from creative_os.services.concepts import propose_concept
from creative_os.services.diversity import audit_batch, fingerprint_concept
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
) -> ModelRun:
    output_name = _output_name(bundle)
    if output_name not in ALLOWED_OUTPUTS:
        raise ReasoningBoundaryError(f"text reasoning is only enabled for {', '.join(sorted(ALLOWED_OUTPUTS))}")
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
) -> list[ModelRun]:
    return [execute_text_reasoning(session, bundle, provider) for provider in providers]


def assert_capability_disabled(capability: str) -> None:
    if capability in DISABLED_CAPABILITIES:
        raise ReasoningBoundaryError(f"{capability} execution is disabled")
    if capability not in {"concept_generation", "story_development_audit", "creative_reasoning"}:
        raise ReasoningBoundaryError(f"{capability} is not a text-reasoning stage")


class _RepairProvider(CreativeReasoningProvider):
    """One logged reformat. It does not call the network again."""

    def __init__(self, parent: CreativeReasoningProvider, text: str) -> None:
        self.name = parent.name
        self._text = text
        self._parent = parent

    def available(self) -> bool:
        return True

    def generate_concepts(self, packet_text: str) -> ReasoningResult:
        return ReasoningResult(text=self._text, model_name=self.name, model_version="reformat")

    def audit_story_development(self, packet_text: str) -> ReasoningResult:
        return ReasoningResult(text=self._text, model_name=self.name, model_version="reformat")


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
    )
    session.add(run)
    session.flush()
    return run


def run_count(session: Session) -> int:
    return int(session.scalar(select(func.count()).select_from(ModelRun)) or 0)
