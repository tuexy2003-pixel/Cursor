"""Persist the exact dry-run context a future provider would receive."""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from creative_os.models import ContextBundle, Creative
from creative_os.models.entities import ImmutableVersionError
from creative_os.services.canonical import stable_digest
from creative_os.services.context_compiler import COMPILER_VERSION, compile_context
from creative_os.util import ensure_utc, utcnow

__all__ = ["COMPILER_VERSION", "ImmutableVersionError", "create_context_bundle", "render_context_text"]


def create_context_bundle(
    session: Session,
    creative: Creative,
    stage: str = "STORY_DEVELOPMENT",
    as_of: datetime | None = None,
    heuristic_budget: int = 24,
) -> ContextBundle:
    moment = ensure_utc(as_of or utcnow())
    payload = compile_context(
        session,
        creative,
        stage=stage,
        heuristic_budget=heuristic_budget,
        as_of=moment,
        include_skill_content=True,
    )
    text = render_context_text(payload)
    digest = stable_digest(payload)
    bundle = ContextBundle(
        creative_id=creative.id,
        requested_stage=str(payload["requested_stage"]),
        created_at=utcnow(),
        as_of=moment,
        story_lock_version_id=(payload.get("current_story_lock_version") or {}).get("id"),
        account_id=creative.account_id,
        campaign_id=creative.campaign_id,
        account_dna_profile_id=(payload.get("account_dna") or {}).get("profile_id"),
        creative_genome_id=(payload.get("creative_genome") or {}).get("id"),
        policy_rule_ids=[item["version"] for item in _policy_items(payload)],
        skill_version_ids=[item["version_id"] for item in payload["skill_versions"]],
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


def render_context_text(payload: dict[str, Any]) -> str:
    lines = [
        f"STAGE {payload['requested_stage']}",
        f"AS_OF {payload['as_of']}",
        f"COMPILER {payload['compiler_version']}",
        "PROVIDER_EXECUTION NOT_IMPLEMENTED",
        "",
    ]
    lock = payload.get("current_story_lock_version") or {}
    lines.append(f"STORY_LOCK v{lock.get('version_number')} {lock.get('id')} hash={lock.get('document_hash')}")
    dna = payload.get("account_dna") or {}
    lines.append(f"ACCOUNT_DNA {dna.get('profile_id')} version={dna.get('version')}")
    genome = payload.get("creative_genome") or {}
    lines.append(f"GENOME {genome.get('id')} version={genome.get('version')}")
    lines.append("")
    for label, key in (
        ("GLOBAL_INVARIANT", "global_invariants"),
        ("PROGRAM", "program_policies"),
        ("ACCOUNT", "account_policies"),
        ("CAMPAIGN", "campaign_policies"),
        ("CREATIVE_LOCK", "creative_locks"),
    ):
        for item in payload.get(key) or []:
            lines.append(f"{label} {item['code']} {item['version']} {item['authority']}")
            lines.append(item.get("text") or "")
            lines.append("")
    for skill in payload.get("skill_versions") or []:
        lines.append(f"SKILL {skill['slug']} {skill['version_id']} {skill['version']} {skill['content_hash']}")
        lines.append(skill.get("content") or "")
        lines.append("")
    for item in payload.get("excluded_for_token_budget") or []:
        lines.append(
            f"EXCLUDED {item.get('code') or item.get('slug') or item.get('name')} {item.get('reason_excluded')}"
        )
    return "\n".join(lines).strip() + "\n"


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
