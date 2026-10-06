"""Paid text-reasoning gate. A configured key is not permission to spend."""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from creative_os.config import get_settings
from creative_os.models import (
    ContextBundle,
    ModelRun,
    ProviderInvocation,
    RunAuthorization,
)
from creative_os.providers.reasoning import MAX_PROVIDERS_PER_COMPARISON, CreativeReasoningProvider
from creative_os.util import ensure_utc, utcnow

NETWORK_ATTEMPT = 1


class AuthorizationError(ValueError):
    pass


def execution_gate_view(session: Session) -> dict[str, Any]:
    settings = get_settings()
    return {
        "live_text_reasoning_enabled": settings.live_text_reasoning_enabled,
        "daily_run_limit": settings.text_reasoning_daily_run_limit,
        "daily_network_attempts": daily_network_attempts(session),
        "max_providers": min(settings.text_reasoning_max_providers, MAX_PROVIDERS_PER_COMPARISON),
        "max_input_tokens": settings.text_reasoning_max_input_tokens,
        "max_output_tokens": settings.text_reasoning_max_output_tokens,
        "estimated_cost_status": "UNKNOWN",
    }


def daily_network_attempts(session: Session, moment: datetime | None = None) -> int:
    start = _day_start(moment or utcnow())
    count = session.scalar(
        select(func.count())
        .select_from(ProviderInvocation)
        .where(
            ProviderInvocation.network_attempts >= NETWORK_ATTEMPT,
            ProviderInvocation.created_at >= start,
        )
    )
    return int(count or 0)


def preflight(session: Session, bundle: ContextBundle, provider: CreativeReasoningProvider) -> dict[str, Any]:
    settings = get_settings()
    text = bundle.compiled_text or ""
    characters = len(text)
    estimated = max(1, characters // 4) if characters else 0
    task = (bundle.compiled_payload or {}).get("task") or {}
    stage = str(task.get("expected_output_type") or bundle.requested_stage)
    status = provider.readiness()
    if status == "READY" and estimated > settings.text_reasoning_max_input_tokens:
        status = "CONTEXT_TOO_LARGE"
    if status == "READY" and daily_network_attempts(session) >= settings.text_reasoning_daily_run_limit:
        status = "DAILY_LIMIT_REACHED"
    return {
        "execution_status": status,
        "provider": provider.name,
        "model": provider.explicit_model(),
        "stage": stage,
        "task_instruction": str(task.get("instruction") or ""),
        "context_bundle_id": bundle.id,
        "context_bundle_hash": bundle.payload_hash,
        "character_count": characters,
        "estimated_tokens": estimated,
        "max_attempts": 1,
        "max_output_tokens": settings.text_reasoning_max_output_tokens,
        "max_input_tokens": settings.text_reasoning_max_input_tokens,
        "daily_network_attempts": daily_network_attempts(session),
        "daily_run_limit": settings.text_reasoning_daily_run_limit,
        "estimated_cost_status": "UNKNOWN",
        "live_enabled": settings.live_text_reasoning_enabled,
        "warning": "THIS WILL MAKE A LIVE PAID PROVIDER REQUEST",
    }


def create_authorization(
    session: Session,
    bundle: ContextBundle,
    provider: CreativeReasoningProvider,
    *,
    actor: str,
    idempotency_key: str,
    allowed_providers: list[str] | None = None,
    max_providers: int = 1,
    notes: str | None = None,
) -> RunAuthorization:
    operator = get_settings().operator_identity
    if actor != operator:
        raise AuthorizationError("only the local operator can authorize a paid run")
    model = provider.explicit_model()
    if model is None:
        raise AuthorizationError("the paid model is not explicitly configured")
    names = allowed_providers or [provider.name]
    if provider.name not in names:
        raise AuthorizationError("the authorization must name the provider that will be called")
    if len(names) > MAX_PROVIDERS_PER_COMPARISON or max_providers > MAX_PROVIDERS_PER_COMPARISON:
        raise AuthorizationError("this phase allows at most 2 providers")
    if max_providers < len(names):
        raise AuthorizationError("max_providers is smaller than the named provider list")
    task = (bundle.compiled_payload or {}).get("task") or {}
    stage = str(task.get("expected_output_type") or "")
    if stage not in {"CONCEPT_GENERATION", "STORY_DEVELOPMENT_AUDIT"}:
        raise AuthorizationError("authorization stage is not an executable text stage")
    settings = get_settings()
    authorization = RunAuthorization(
        context_bundle_id=bundle.id,
        context_bundle_hash=bundle.payload_hash,
        provider_name=provider.name,
        model_name=model,
        stage=stage,
        created_by=operator,
        created_at=utcnow(),
        expires_at=utcnow() + timedelta(hours=1),
        status="AUTHORIZED",
        max_attempts=1,
        attempts_used=0,
        max_output_tokens=settings.text_reasoning_max_output_tokens,
        max_input_tokens=settings.text_reasoning_max_input_tokens,
        max_providers=max_providers,
        allowed_providers=names,
        max_cost=None,
        currency=None,
        notes=notes,
        idempotency_key=idempotency_key,
    )
    existing = session.scalar(
        select(RunAuthorization).where(RunAuthorization.idempotency_key == idempotency_key)
    )
    if existing is not None:
        return existing
    nested = session.begin_nested()
    try:
        session.add(authorization)
        session.flush()
        nested.commit()
    except IntegrityError:
        nested.rollback()
        existing = session.scalar(
            select(RunAuthorization).where(RunAuthorization.idempotency_key == idempotency_key)
        )
        if existing is None:
            raise
        return existing
    return authorization


def find_invocation(session: Session, idempotency_key: str) -> ProviderInvocation | None:
    return session.scalar(
        select(ProviderInvocation).where(ProviderInvocation.idempotency_key == idempotency_key)
    )


def claim_invocation(
    session: Session,
    authorization: RunAuthorization,
    provider: CreativeReasoningProvider,
    bundle: ContextBundle,
    idempotency_key: str,
) -> tuple[ProviderInvocation | None, ModelRun | None, bool]:
    """Return (invocation, existing_run, created). created is false when the key already exists."""
    existing = find_invocation(session, idempotency_key)
    if existing is not None:
        run = None if existing.model_run_id is None else session.get(ModelRun, existing.model_run_id)
        return existing, run, False
    model = provider.explicit_model() or authorization.model_name
    invocation = ProviderInvocation(
        idempotency_key=idempotency_key,
        authorization_id=authorization.id,
        provider_name=provider.name,
        model_name=model,
        context_bundle_id=bundle.id,
        context_bundle_hash=bundle.payload_hash,
        status="CLAIMED",
        network_attempts=0,
        created_at=utcnow(),
    )
    nested = session.begin_nested()
    try:
        session.add(invocation)
        session.flush()
        nested.commit()
    except IntegrityError:
        nested.rollback()
        existing = find_invocation(session, idempotency_key)
        if existing is None:
            raise
        run = None if existing.model_run_id is None else session.get(ModelRun, existing.model_run_id)
        return existing, run, False
    return invocation, None, True


def authorization_block(
    session: Session,
    authorization: RunAuthorization | None,
    bundle: ContextBundle,
    provider: CreativeReasoningProvider,
    stage: str,
) -> str | None:
    if authorization is None:
        return "AUTHORIZATION_REQUIRED"
    if authorization.status in {"CANCELLED", "EXPIRED", "CONSUMED"}:
        return "AUTHORIZATION_REQUIRED"
    if ensure_utc(authorization.expires_at) <= utcnow():
        authorization.status = "EXPIRED"
        session.flush()
        return "AUTHORIZATION_REQUIRED"
    if authorization.context_bundle_id != bundle.id or authorization.context_bundle_hash != bundle.payload_hash:
        return "AUTHORIZATION_MISMATCH"
    allowed = set(authorization.allowed_providers or [])
    if provider.name not in allowed:
        return "AUTHORIZATION_MISMATCH"
    model = provider.explicit_model()
    if model is None or model != authorization.model_name:
        return "AUTHORIZATION_MISMATCH"
    if authorization.stage != stage:
        return "AUTHORIZATION_MISMATCH"
    if _provider_attempts(session, authorization, provider.name) >= authorization.max_attempts:
        return "AUTHORIZATION_REQUIRED"
    unknown = session.scalar(
        select(ProviderInvocation.id).where(
            ProviderInvocation.authorization_id == authorization.id,
            ProviderInvocation.provider_name == provider.name,
            ProviderInvocation.status == "UNKNOWN_PROVIDER_OUTCOME",
        )
    )
    if unknown is not None:
        return "UNKNOWN_PROVIDER_OUTCOME"
    characters = len(bundle.compiled_text or "")
    estimated = max(1, characters // 4) if characters else 0
    ceiling = authorization.max_input_tokens or get_settings().text_reasoning_max_input_tokens
    if estimated > ceiling:
        return "CONTEXT_TOO_LARGE"
    if daily_network_attempts(session) >= get_settings().text_reasoning_daily_run_limit:
        return "DAILY_LIMIT_REACHED"
    return None


def mark_requesting(session: Session, invocation: ProviderInvocation, authorization: RunAuthorization) -> None:
    invocation.status = "REQUESTING"
    invocation.network_attempts = NETWORK_ATTEMPT
    invocation.started_at = utcnow()
    authorization.attempts_used += 1
    session.flush()
    session.commit()


def finish_authorization(session: Session, authorization: RunAuthorization) -> None:
    names = list(authorization.allowed_providers or [authorization.provider_name])
    if names and all(
        _provider_attempts(session, authorization, name) >= authorization.max_attempts for name in names
    ):
        authorization.status = "CONSUMED"


def _provider_attempts(session: Session, authorization: RunAuthorization, provider_name: str) -> int:
    count = session.scalar(
        select(func.count())
        .select_from(ProviderInvocation)
        .where(
            ProviderInvocation.authorization_id == authorization.id,
            ProviderInvocation.provider_name == provider_name,
            ProviderInvocation.network_attempts >= NETWORK_ATTEMPT,
        )
    )
    return int(count or 0)


def usage_summary(session: Session, moment: datetime | None = None) -> dict[str, Any]:
    now = moment or utcnow()
    windows = {
        "today": _day_start(now),
        "last_7_days": now - timedelta(days=7),
        "lifetime": None,
    }
    runs = session.scalars(select(ModelRun)).all()
    report: dict[str, Any] = {}
    for name, start in windows.items():
        grouped: dict[str, dict[str, Any]] = {}
        for run in runs:
            started = ensure_utc(run.started_at)
            if start is not None and started < ensure_utc(start):
                continue
            key = run.provider_model_name or "unknown"
            bucket = grouped.setdefault(
                key,
                {
                    "provider_model": key,
                    "run_count": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cached_tokens": 0,
                    "known_cost": None,
                    "unknown_cost_runs": 0,
                    "provider_errors": 0,
                    "parse_failures": 0,
                },
            )
            bucket["run_count"] += 1
            bucket["input_tokens"] += run.input_tokens or 0
            bucket["output_tokens"] += run.output_tokens or 0
            bucket["cached_tokens"] += run.cached_tokens or 0
            if run.cost is None:
                bucket["unknown_cost_runs"] += 1
            else:
                bucket["known_cost"] = float(run.cost) + float(bucket["known_cost"] or 0)
            if run.status == "PROVIDER_ERROR":
                bucket["provider_errors"] += 1
            if run.status == "PARSE_FAILED":
                bucket["parse_failures"] += 1
        report[name] = sorted(grouped.values(), key=lambda item: item["provider_model"])
    return report


def _day_start(moment: datetime) -> datetime:
    moment = ensure_utc(moment)
    return moment.replace(hour=0, minute=0, second=0, microsecond=0)
