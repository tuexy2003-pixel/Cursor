"""Persist the exact dry-run context a future provider would receive."""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from creative_os.models import ContextBundle, Creative, CreativeTask
from creative_os.models.entities import ImmutableVersionError
from creative_os.services.canonical import stable_digest
from creative_os.services.context_compiler import COMPILER_VERSION, compile_context
from creative_os.services.provider_packet import render_context_text
from creative_os.services.tasks import consume_task
from creative_os.util import ensure_utc, utcnow

__all__ = ["COMPILER_VERSION", "ImmutableVersionError", "create_context_bundle", "render_context_text"]


def create_context_bundle(
    session: Session,
    creative: Creative | None = None,
    stage: str = "STORY_DEVELOPMENT",
    as_of: datetime | None = None,
    heuristic_budget: int = 24,
    task: CreativeTask | None = None,
) -> ContextBundle:
    if task is None:
        raise ValueError("a context bundle requires a creative task")
    moment = ensure_utc(as_of or utcnow())
    consume_task(task)
    payload = compile_context(
        session,
        creative,
        stage=stage,
        heuristic_budget=heuristic_budget,
        as_of=moment,
        include_skill_content=True,
        task=task,
    )
    text = render_context_text(payload)
    digest = stable_digest(payload)
    scope = payload.get("scope") or {}
    account = scope.get("account") or {}
    campaign = scope.get("campaign") or {}
    bundle = ContextBundle(
        creative_id=None if creative is None else creative.id,
        creative_task_id=task.id,
        requested_stage=str(payload["requested_stage"]),
        created_at=utcnow(),
        as_of=moment,
        story_lock_version_id=(payload.get("current_story_lock_version") or {}).get("id"),
        account_id=account.get("id"),
        campaign_id=campaign.get("id"),
        account_dna_profile_id=(payload.get("account_dna") or {}).get("profile_id"),
        creative_genome_id=(payload.get("creative_genome") or {}).get("id"),
        policy_rule_ids=[item["version"] for item in _policy_items(payload)],
        skill_version_ids=[item["version_id"] for item in payload["skill_versions"] if item.get("version_id")],
        benchmark_ids=[item["version"] for item in payload["benchmarks"]],
        reference_ids=[item["version"] for item in payload["references"]],
        mechanic_as_of=moment,
        compiled_payload=payload,
        compiled_text=text,
        payload_hash=digest,
        compiler_version=COMPILER_VERSION,
        size_estimate=len(text),
        token_estimate=max(1, len(text) // 4) if text else 0,
        status="COMPILED",
    )
    session.add(bundle)
    session.flush()
    return bundle


def _policy_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for key in (
        "global_invariants",
        "program_policies",
        "account_policies",
        "campaign_policies",
        "creative_locks",
    ):
        items.extend(payload.get(key) or [])
    return items
