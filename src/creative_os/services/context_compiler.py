"""Dry-run context package. This does not call a provider."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import (
    AccountDnaObservation,
    AccountDnaProfile,
    BenchmarkCreative,
    CommentDoor,
    Creative,
    CreativeGenome,
    Ecosystem,
    GenomeFacet,
    ReferenceBank,
    SkillArtifact,
    SkillVersion,
    StoryLockVersion,
)
from creative_os.schemas.story_lock import StoryLockDocument
from creative_os.services.mechanics import mechanic_report
from creative_os.services.policy_resolver import resolve_policy_detail
from creative_os.util import ensure_utc, utcnow

COMPILER_VERSION = "context-compiler-0.2.1"

STAGE_SKILLS: dict[str, set[str]] = {
    "RESEARCH": {
        "live-heat-scout",
        "object-culture-scout",
        "find-purchase-screens-on-pinterest",
        "adaptation-blitz-match",
    },
    "CONCEPT_GENERATION": {
        "commercial-aware-synthesis",
        "getting-started",
        "commerce-world-mapper",
    },
    "STORY_DEVELOPMENT": {
        "story-development",
        "story-conflict-scout",
        "synthetic-story-generator",
        "chat-story-slideshow",
    },
    "PRODUCTION_ROUTING": {"visual-surface-acquisition", "source-card"},
    "PRODUCTION_QA": {"production-spec-qa", "ios-26-production-normalization"},
    "PERFORMANCE_INTERPRETATION": set(),
}
STAGE_ALIASES = {
    "story": "STORY_DEVELOPMENT",
    "production": "PRODUCTION_QA",
    "research": "RESEARCH",
    "full": "PIPELINE",
}


def canonical_stage(stage: str) -> str:
    name = STAGE_ALIASES.get(stage, stage)
    if name != "PIPELINE" and name not in STAGE_SKILLS:
        raise ValueError(f"unknown context stage: {stage}")
    return name


def required_slugs(stage: str) -> set[str]:
    name = canonical_stage(stage)
    if name == "PIPELINE":
        required: set[str] = set()
        for slugs in STAGE_SKILLS.values():
            required.update(slugs)
        return required
    return set(STAGE_SKILLS[name])


def compile_context(
    session: Session,
    creative: Creative,
    stage: str = "full",
    heuristic_budget: int = 24,
    as_of: datetime | None = None,
    include_skill_content: bool = False,
) -> dict[str, Any]:
    moment = ensure_utc(as_of or utcnow())
    stage_name = canonical_stage(stage)
    rules, policy_excluded = resolve_policy_detail(session, creative, moment)
    policy_items = [_rule_item(rule) for rule in rules]
    invariants = [item for item in policy_items if item["rule_kind"] == "INVARIANT"]
    optional = [item for item in policy_items if item["rule_kind"] != "INVARIANT"]
    kept_optional = optional[:heuristic_budget]
    excluded = [{**item, "reason_excluded": "heuristic token budget"} for item in optional[heuristic_budget:]]
    for rule, reason in policy_excluded:
        excluded.append({**_rule_item(rule), "reason_excluded": reason})
    included_rules = invariants + kept_optional
    skills, skill_excluded = _skills(session, stage_name, include_skill_content)
    excluded.extend(skill_excluded)
    lock = _lock(session, creative)
    dna = _dna(session, creative)
    genome = _genome(session, creative, lock)
    benchmarks, benchmark_excluded = _benchmarks(session, creative, heuristic_budget)
    excluded.extend(benchmark_excluded)
    document = StoryLockDocument.model_validate(lock.content_json) if lock else None
    return {
        "dry_run": True,
        "provider_execution": "NOT_IMPLEMENTED",
        "compiler_version": COMPILER_VERSION,
        "as_of": moment.isoformat(),
        "requested_stage": stage_name,
        "creative": {"id": creative.id, "name": creative.name, "slug": creative.slug},
        "current_story_lock_version": None
        if lock is None
        else {
            "id": lock.id,
            "version_number": lock.version_number,
            "document_hash": lock.document_hash,
            "source_hash": lock.source_hash,
            "authority": "approved story lock",
            "reason_included": "current approved pointer",
        },
        "global_invariants": [item for item in included_rules if item["scope"] == "GLOBAL"],
        "program_policies": [item for item in included_rules if item["scope"] == "PROGRAM"],
        "account_policies": [item for item in included_rules if item["scope"] == "ACCOUNT"],
        "campaign_policies": [item for item in included_rules if item["scope"] == "CAMPAIGN"],
        "creative_locks": [item for item in included_rules if item["scope"] == "CREATIVE"],
        "skill_versions": skills,
        "account_dna": dna,
        "creative_genome": genome,
        "benchmarks": benchmarks,
        "mechanic_context": mechanic_report(session, creative.account_id, as_of=moment),
        "references": _references(session, creative),
        "comment_doors": _doors(session, lock),
        "continuity": []
        if document is None
        else [
            {"slide_index": fact.slide_index, "field": fact.field, "value": fact.value}
            for fact in document.continuity
        ],
        "excluded_for_token_budget": excluded,
    }


def _rule_item(rule: Any) -> dict[str, Any]:
    authority = "hard invariant" if rule.rule_kind == "INVARIANT" else rule.rule_kind.lower()
    return {
        "code": rule.code,
        "text": rule.text,
        "source": rule.source_path,
        "scope": rule.scope_level,
        "scope_id": rule.scope_id,
        "reason_included": f"resolved {rule.scope_level} {rule.rule_kind} for {rule.code}",
        "version": rule.id,
        "authority": authority,
        "rule_kind": rule.rule_kind,
        "content_hash": rule.content_hash,
        "approval_state": rule.approval_state,
    }


def _skills(
    session: Session,
    stage: str,
    include_content: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    artifacts = session.scalars(select(SkillArtifact).order_by(SkillArtifact.slug)).all()
    wanted = required_slugs(stage)
    by_slug = {artifact.slug: artifact for artifact in artifacts}
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for slug in sorted(wanted):
        artifact = by_slug.get(slug)
        if artifact is None or not artifact.current_version_id:
            excluded.append(
                {
                    "slug": slug,
                    "reason_excluded": "required stage skill has no current version",
                    "authority": "active skill",
                }
            )
            continue
        version = session.get(SkillVersion, artifact.current_version_id)
        if version is None or not version.status.startswith("ACTIVE"):
            excluded.append(
                {
                    "slug": slug,
                    "reason_excluded": "required stage skill is not active",
                    "authority": "active skill",
                    "version_id": None if version is None else version.id,
                }
            )
            continue
        included.append(_skill_item(artifact, version, stage, include_content))
    for artifact in artifacts:
        if artifact.slug in wanted or not artifact.current_version_id:
            continue
        version = session.get(SkillVersion, artifact.current_version_id)
        if version is None or not version.status.startswith("ACTIVE"):
            continue
        item = _skill_item(artifact, version, stage, include_content=False)
        excluded.append({**item, "reason_excluded": f"not part of stage {stage}"})
    return included, excluded


def _skill_item(
    artifact: SkillArtifact,
    version: SkillVersion,
    stage: str,
    include_content: bool,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "slug": artifact.slug,
        "source": version.source_path,
        "scope": version.scope_level,
        "reason_included": f"required skill for stage {stage}",
        "version": version.version_label,
        "version_id": version.id,
        "authority": "active skill",
        "content_hash": version.content_hash,
        "rule_kind": version.rule_kind,
    }
    if include_content:
        item["content"] = version.content
    return item


def _lock(session: Session, creative: Creative) -> StoryLockVersion | None:
    if not creative.current_approved_story_lock_version_id:
        return None
    return session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)


def _dna(session: Session, creative: Creative) -> dict[str, Any] | None:
    if not creative.account_id:
        return None
    from creative_os.models import Account

    account = session.get(Account, creative.account_id)
    if account is None or not account.current_approved_dna_profile_id:
        return None
    profile = session.get(AccountDnaProfile, account.current_approved_dna_profile_id)
    if profile is None or profile.approval_state != "APPROVED":
        return None
    observations = session.scalars(
        select(AccountDnaObservation)
        .where(AccountDnaObservation.profile_id == profile.id)
        .order_by(AccountDnaObservation.field_name)
    ).all()
    return {
        "profile_id": profile.id,
        "version_number": profile.version_number,
        "origin": profile.origin,
        "approval_state": profile.approval_state,
        "source": "account.current_approved_dna_profile_id",
        "scope": "ACCOUNT",
        "reason_included": "explicit current-approved DNA pointer",
        "authority": "approved account dna",
        "version": str(profile.version_number),
        "observations": [
            {
                "field_name": row.field_name,
                "value": row.value,
                "evidence_kind": row.evidence_kind,
                "sample_size": row.sample_size,
            }
            for row in observations
        ],
    }


def _genome(session: Session, creative: Creative, lock: StoryLockVersion | None) -> dict[str, Any] | None:
    if not creative.current_genome_id or lock is None:
        return None
    genome = session.get(CreativeGenome, creative.current_genome_id)
    if genome is None:
        return None
    if genome.source_story_lock_version_id != lock.id:
        return None
    if genome.approval_state != "APPROVED":
        return None
    facets = session.scalars(
        select(GenomeFacet).where(GenomeFacet.genome_id == genome.id).order_by(GenomeFacet.dimension)
    ).all()
    return {
        "id": genome.id,
        "version_label": genome.version_label,
        "source_story_lock_version_id": genome.source_story_lock_version_id,
        "origin": genome.origin,
        "approval_state": genome.approval_state,
        "source": genome.version_label,
        "scope": "CREATIVE",
        "reason_included": "genome bound to the current approved story lock",
        "authority": genome.origin,
        "version": genome.version_label,
        "facets": [
            {"dimension": row.dimension, "value": row.value, "assignment": row.assignment} for row in facets
        ],
    }


def _benchmarks(
    session: Session, creative: Creative, budget: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ecosystem = session.get(Ecosystem, creative.ecosystem_id) if creative.ecosystem_id else None
    code = ecosystem.code if ecosystem else None
    rows = session.scalars(
        select(BenchmarkCreative).where(BenchmarkCreative.holdout.is_(False)).order_by(BenchmarkCreative.name)
    ).all()
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for row in rows:
        if code and row.ecosystem_code not in {None, code}:
            continue
        item = {
            "name": row.name,
            "source": row.source_path,
            "scope": "PROGRAM",
            "reason_included": "non-holdout benchmark",
            "version": row.id,
            "authority": "reference example",
            "category": row.category,
        }
        if len(included) >= budget:
            excluded.append({**item, "reason_excluded": "heuristic token budget"})
            continue
        included.append(item)
    return included, excluded


def _references(session: Session, creative: Creative) -> list[dict[str, Any]]:
    ecosystem = session.get(Ecosystem, creative.ecosystem_id) if creative.ecosystem_id else None
    rows = session.scalars(select(ReferenceBank).order_by(ReferenceBank.name)).all()
    items = []
    for row in rows:
        if ecosystem and row.ecosystem_id not in {None, ecosystem.id}:
            continue
        items.append(
            {
                "name": row.name,
                "source": row.original_path,
                "scope": "PROGRAM",
                "reason_included": "reference metadata only",
                "version": row.id,
                "authority": "reference",
            }
        )
    return items


def _doors(session: Session, lock: StoryLockVersion | None) -> list[dict[str, Any]]:
    if lock is None:
        return []
    rows = session.scalars(
        select(CommentDoor)
        .where(CommentDoor.story_lock_version_id == lock.id)
        .order_by(CommentDoor.kind, CommentDoor.text)
    ).all()
    return [
        {
            "kind": row.kind,
            "text": row.text,
            "source": "comment_doors",
            "scope": "CREATIVE",
            "reason_included": "doors projected from the current story lock",
            "version": lock.id,
            "authority": "approved story lock",
        }
        for row in rows
    ]
