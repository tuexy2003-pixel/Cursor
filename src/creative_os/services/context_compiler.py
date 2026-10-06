"""Dry-run context package. This does not call a provider."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import (
    Account,
    AccountDnaObservation,
    AccountDnaProfile,
    Asset,
    BenchmarkCreative,
    Campaign,
    CommentDoor,
    ConceptCandidate,
    Creative,
    CreativeGenome,
    CreativeTask,
    Ecosystem,
    GenomeFacet,
    Program,
    ReferenceBank,
    SkillArtifact,
    SkillVersion,
    StoryLockVersion,
)
from creative_os.schemas.contracts import ConceptGenerationResult, StoryDevelopmentAuditResult
from creative_os.schemas.story_lock import StoryLockDocument
from creative_os.services.mechanics import mechanic_report
from creative_os.services.policy_resolver import resolve_policy_detail
from creative_os.services.provider_packet import render_sections, section_sizes
from creative_os.services.scope import ContextScope, scope_from_creative
from creative_os.services.tasks import task_scope
from creative_os.util import ensure_utc, utcnow

COMPILER_VERSION = "context-compiler-0.3.0"

SCOPE_SPECIFICITY = {"CREATIVE": 0, "CAMPAIGN": 1, "ACCOUNT": 2, "PROGRAM": 3, "GLOBAL": 4}
KIND_RANK = {"PREFERENCE": 0, "HEURISTIC": 1}
CATEGORY_RANK = {"WINNER": 0, "WEAK": 1, "FAILURE": 2}
PRODUCTION_STAGES = {"PRODUCTION_ROUTING", "PRODUCTION_QA"}


@dataclass(frozen=True)
class StageSkill:
    slug: str
    role: str


STAGE_REGISTRY: dict[str, tuple[StageSkill, ...]] = {
    "RESEARCH": (
        StageSkill("story-conflict-scout", "REQUIRED"),
        StageSkill("object-culture-scout", "REQUIRED"),
        StageSkill("live-heat-scout", "REQUIRED"),
        StageSkill("source-card", "SUPPORTING"),
        StageSkill("commerce-world-mapper", "SUPPORTING"),
    ),
    "CONCEPT_GENERATION": (
        StageSkill("synthetic-story-generator", "REQUIRED"),
        StageSkill("commercial-aware-synthesis", "REQUIRED"),
        StageSkill("adaptation-blitz-match", "REQUIRED"),
    ),
    "STORY_DEVELOPMENT": (
        StageSkill("story-development", "REQUIRED"),
        StageSkill("chat-story-slideshow", "OPTIONAL_SPECIALIST"),
    ),
    "PRODUCTION_ROUTING": (
        StageSkill("production-spec-qa", "REQUIRED"),
        StageSkill("visual-surface-acquisition", "REQUIRED"),
        StageSkill("find-purchase-screens-on-pinterest", "REQUIRED"),
    ),
    "PRODUCTION_QA": (
        StageSkill("production-spec-qa", "REQUIRED"),
        StageSkill("ios-26-production-normalization", "REQUIRED"),
    ),
    "PERFORMANCE_INTERPRETATION": (),
}
STAGE_ALIASES = {
    "story": "STORY_DEVELOPMENT",
    "production": "PRODUCTION_QA",
    "research": "RESEARCH",
    "full": "PIPELINE",
}


def canonical_stage(stage: str) -> str:
    name = STAGE_ALIASES.get(stage, stage)
    if name != "PIPELINE" and name not in STAGE_REGISTRY:
        raise ValueError(f"unknown context stage: {stage}")
    return name


def stage_entries(stage: str) -> tuple[StageSkill, ...]:
    name = canonical_stage(stage)
    if name == "PIPELINE":
        seen: dict[str, StageSkill] = {}
        for entries in STAGE_REGISTRY.values():
            for entry in entries:
                if entry.role == "REQUIRED" and entry.slug not in seen:
                    seen[entry.slug] = entry
        return tuple(seen.values())
    return STAGE_REGISTRY[name]


def required_slugs(stage: str) -> set[str]:
    return {entry.slug for entry in stage_entries(stage) if entry.role == "REQUIRED"}


def compile_context(
    session: Session,
    creative: Creative | None = None,
    stage: str = "full",
    heuristic_budget: int = 24,
    as_of: datetime | None = None,
    include_skill_content: bool = False,
    scope: ContextScope | None = None,
    task: CreativeTask | None = None,
) -> dict[str, Any]:
    moment = ensure_utc(as_of or utcnow())
    if task is not None:
        stage = task.stage
        if scope is None:
            scope = task_scope(task)
        if creative is None and task.creative_id:
            creative = session.get(Creative, task.creative_id)
    elif creative is not None and scope is None:
        scope = scope_from_creative(creative)
    if scope is None:
        raise ValueError("context compilation requires a creative or an explicit scope")
    stage_name = canonical_stage(stage)
    rules, policy_excluded = resolve_policy_detail(session, scope, moment)
    included_rules, budget_excluded = _budget_rules(rules, stage_name, heuristic_budget)
    excluded = budget_excluded
    for rule, reason in policy_excluded:
        excluded.append({**_rule_item(rule), "reason_excluded": reason})
    specialists = _requested_specialists(task)
    skills, skill_excluded, audit, coverage = _skills(session, stage_name, include_skill_content, specialists)
    excluded.extend(skill_excluded)
    lock = _lock(session, creative)
    document = StoryLockDocument.model_validate(lock.content_json) if lock else None
    dna = _dna(session, scope.account_id)
    genome, genome_state = _genome(session, creative, lock)
    benchmarks, benchmark_excluded = _benchmarks(session, scope, heuristic_budget)
    excluded.extend(benchmark_excluded)
    references, assets, reference_excluded = _references(session, scope, creative, stage_name)
    excluded.extend(reference_excluded)
    payload: dict[str, Any] = {
        "dry_run": True,
        "provider_execution": "NOT_IMPLEMENTED",
        "compiler_version": COMPILER_VERSION,
        "as_of": moment.isoformat(),
        "requested_stage": stage_name,
        "skill_coverage": coverage,
        "task": _task_payload(task),
        "scope": _identity(session, scope, creative),
        "output_contract": _output_contract(task, stage_name),
        "current_story_lock_version": _lock_payload(lock, document),
        "global_invariants": [item for item in included_rules if item["scope"] == "GLOBAL"],
        "program_policies": [item for item in included_rules if item["scope"] == "PROGRAM"],
        "account_policies": [item for item in included_rules if item["scope"] == "ACCOUNT"],
        "campaign_policies": [item for item in included_rules if item["scope"] == "CAMPAIGN"],
        "creative_locks": [item for item in included_rules if item["scope"] == "CREATIVE"],
        "skill_versions": skills,
        "skill_dependency_audit": audit,
        "account_dna": dna,
        "creative_genome": genome,
        "genome_state": genome_state,
        "selected_concept": _selected_concept(session, creative),
        "benchmarks": benchmarks,
        "mechanic_context": mechanic_report(
            session,
            scope.account_id,
            as_of=moment,
            subject_creative_id=scope.creative_id,
            exclude_holdouts=True,
        ),
        "references": references,
        "assets": assets,
        "comment_doors": _doors(session, lock, document),
        "continuity": []
        if document is None
        else [
            {"slide_index": fact.slide_index, "field": fact.field, "value": fact.value}
            for fact in document.continuity
        ],
        "excluded_for_token_budget": excluded,
    }
    payload["section_sizes"] = section_sizes(render_sections(payload))
    return payload


def _task_payload(task: CreativeTask | None) -> dict[str, Any] | None:
    if task is None:
        return None
    return {
        "id": task.id,
        "stage": task.stage,
        "instruction": task.instruction,
        "constraints": task.constraints,
        "input_refs": task.input_refs,
        "status": task.status,
        "expected_output_type": task.expected_output_type,
        "created_by": task.created_by,
    }


def _output_contract(task: CreativeTask | None, stage: str) -> dict[str, Any] | None:
    name = None if task is None else task.expected_output_type
    if name is None and stage == "CONCEPT_GENERATION":
        name = "CONCEPT_GENERATION"
    if name is None and stage == "STORY_DEVELOPMENT":
        name = "STORY_DEVELOPMENT_AUDIT"
    model: type[ConceptGenerationResult] | type[StoryDevelopmentAuditResult]
    if name == "CONCEPT_GENERATION":
        model = ConceptGenerationResult
        instructions = (
            "Return ConceptGenerationResult JSON only. Each concept is a proposal for human review. "
            "It is not a StoryLock. Leave unknown fields null. Do not copy holdout or benchmark stories."
        )
    elif name == "STORY_DEVELOPMENT_AUDIT":
        model = StoryDevelopmentAuditResult
        instructions = (
            "Return StoryDevelopmentAuditResult JSON only. This is a diagnosis and proposal. "
            "Do not mutate the StoryLock. Preserve decisions that are already working."
        )
    else:
        return None
    return {"name": name, "instructions": instructions, "json_schema": model.model_json_schema()}


def _requested_specialists(task: CreativeTask | None) -> set[str]:
    if task is None or not isinstance(task.constraints, dict):
        return set()
    raw = task.constraints.get("specialist_skills") or []
    if not isinstance(raw, list):
        return set()
    return {str(item) for item in raw}


def _authoritative(item: dict[str, Any]) -> bool:
    if item["rule_kind"] in {"INVARIANT", "LOCKED_VALUE"}:
        return True
    heading = str(item.get("title") or "")
    return bool(re.match(r"^(proof|rights|approval)\b", heading.strip(), re.IGNORECASE))


def _budget_rules(
    rules: list[Any], stage: str, budget: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    protected: list[dict[str, Any]] = []
    optional: list[dict[str, Any]] = []
    for rule in rules:
        item = _rule_item(rule)
        if _authoritative(item):
            item["priority"] = "authoritative"
            item["reason_included"] = f"{item['reason_included']}; retained regardless of token budget"
            protected.append(item)
        else:
            optional.append(item)
    optional.sort(key=lambda item: _optional_key(item, stage))
    for index, item in enumerate(optional):
        item["priority"] = _priority_label(item, stage, index)
    kept = optional[: max(budget, 0)]
    dropped = optional[max(budget, 0) :]
    excluded = [{**item, "reason_excluded": "heuristic token budget"} for item in dropped]
    return protected + kept, excluded


def _optional_key(item: dict[str, Any], stage: str) -> tuple[Any, ...]:
    return (
        SCOPE_SPECIFICITY.get(item["scope"], 9),
        KIND_RANK.get(item["rule_kind"], 5),
        0 if _stage_relevant(item, stage) else 1,
        item["code"],
        item["version"],
    )


def _priority_label(item: dict[str, Any], stage: str, index: int) -> str:
    key = _optional_key(item, stage)
    return f"scope={key[0]};kind={key[1]};stage={key[2]};order={index};code={item['code']}"


def _stage_relevant(item: dict[str, Any], stage: str) -> bool:
    blob = f"{item['code']} {item.get('text', '')}".lower()
    return any(entry.slug in blob for entry in stage_entries(stage))


def _rule_item(rule: Any) -> dict[str, Any]:
    authority = "hard invariant" if rule.rule_kind == "INVARIANT" else rule.rule_kind.lower()
    return {
        "code": rule.code,
        "title": rule.title,
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
    specialists: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], str]:
    artifacts = session.scalars(select(SkillArtifact).order_by(SkillArtifact.slug)).all()
    by_slug = {artifact.slug: artifact for artifact in artifacts}
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    selected: set[str] = set()
    entries = stage_entries(stage)
    coverage = "MISSING_DEDICATED_SKILL" if stage == "PERFORMANCE_INTERPRETATION" else "COVERED"
    for entry in entries:
        if entry.role == "OPTIONAL_SPECIALIST" and entry.slug not in specialists:
            excluded.append(
                {
                    "slug": entry.slug,
                    "skill_role": entry.role,
                    "reason_excluded": "optional specialist not requested for this task",
                    "authority": "stage registry",
                }
            )
            continue
        item, reason = _select_skill(session, by_slug.get(entry.slug), entry, stage, include_content)
        if item is None:
            excluded.append(
                {
                    "slug": entry.slug,
                    "skill_role": entry.role,
                    "reason_excluded": reason,
                    "authority": "stage registry",
                }
            )
            continue
        included.append(item)
        selected.add(entry.slug)
    for artifact in artifacts:
        if artifact.slug in selected or not artifact.current_version_id:
            continue
        version = session.get(SkillVersion, artifact.current_version_id)
        if version is None or not _status_usable(version.status, "REQUIRED"):
            continue
        if any(entry.slug == artifact.slug for entry in entries):
            continue
        excluded.append(
            {
                "slug": artifact.slug,
                "skill_role": None,
                "version_id": version.id,
                "reason_excluded": f"not part of stage {stage}",
                "authority": "stage registry",
            }
        )
    audit = _dependency_audit(included, stage)
    return included, excluded, audit, coverage


def _select_skill(
    session: Session,
    artifact: SkillArtifact | None,
    entry: StageSkill,
    stage: str,
    include_content: bool,
) -> tuple[dict[str, Any] | None, str]:
    if artifact is None or not artifact.current_version_id:
        return None, "stage skill has no current version"
    version = session.get(SkillVersion, artifact.current_version_id)
    if version is None or not _status_usable(version.status, entry.role):
        if version is not None and version.status.upper().startswith("LEGACY"):
            return None, "legacy skill is excluded outside an explicit onboarding task"
        status = "missing" if version is None else version.status
        return None, f"{entry.role.lower()} stage skill is not usable with status {status}"
    return _skill_item(artifact, version, stage, entry.role, include_content), ""


def _status_usable(status: str, role: str) -> bool:
    label = status.upper()
    if label.startswith("LEGACY"):
        return False
    if role == "REQUIRED":
        return label.startswith("ACTIVE")
    if role in {"SUPPORTING", "OPTIONAL_SPECIALIST"}:
        return label.startswith("ACTIVE") or label.startswith("SUPPORTING")
    return False


def _skill_item(
    artifact: SkillArtifact,
    version: SkillVersion,
    stage: str,
    role: str,
    include_content: bool,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "slug": artifact.slug,
        "skill_role": role,
        "source": version.source_path,
        "scope": version.scope_level,
        "reason_included": f"{role.lower()} skill for stage {stage}",
        "version": version.version_label,
        "version_id": version.id,
        "authority": "stage registry",
        "content_hash": version.content_hash,
        "rule_kind": version.rule_kind,
        "dependencies": list(version.dependencies or []),
    }
    if include_content:
        item["content"] = version.content
    return item


def _dependency_audit(included: list[dict[str, Any]], stage: str) -> list[dict[str, Any]]:
    selected = {item["slug"] for item in included}
    rows: list[dict[str, Any]] = []
    for item in included:
        if item["skill_role"] != "REQUIRED":
            continue
        for dependency in item.get("dependencies") or []:
            slug = str(dependency)
            if slug in selected:
                state = "included"
                reason = "dependency skill is in this stage packet"
            else:
                state = "intentionally_not_included"
                reason = (
                    "stage registry did not select this dependency; "
                    "structured creative state is carried separately "
                    "when a StoryLock or DNA profile is in scope"
                )
            rows.append(
                {
                    "skill": item["slug"],
                    "dependency": slug,
                    "state": state,
                    "reason": reason,
                    "stage": stage,
                }
            )
    return rows


def _lock(session: Session, creative: Creative | None) -> StoryLockVersion | None:
    if creative is None or not creative.current_approved_story_lock_version_id:
        return None
    return session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)


def _lock_payload(lock: StoryLockVersion | None, document: StoryLockDocument | None) -> dict[str, Any] | None:
    if lock is None or document is None:
        return None
    return {
        "id": lock.id,
        "version_number": lock.version_number,
        "document_hash": lock.document_hash,
        "source_hash": lock.source_hash,
        "approval_state": lock.approval_state,
        "authority": "approved story lock",
        "reason_included": "current approved pointer",
        "document": document.model_dump(mode="json"),
        "markdown": lock.content_markdown,
    }


def _identity(session: Session, scope: ContextScope, creative: Creative | None) -> dict[str, Any]:
    program = session.get(Program, scope.program_id) if scope.program_id else None
    account = session.get(Account, scope.account_id) if scope.account_id else None
    campaign = session.get(Campaign, scope.campaign_id) if scope.campaign_id else None
    ecosystem = session.get(Ecosystem, scope.ecosystem_id) if scope.ecosystem_id else None
    return {
        "program": None if program is None else {"id": program.id, "slug": program.slug, "name": program.name},
        "account": None if account is None else {"id": account.id, "slug": account.slug, "name": account.name},
        "campaign": None
        if campaign is None
        else {"id": campaign.id, "slug": campaign.slug, "name": campaign.name},
        "ecosystem": None
        if ecosystem is None
        else {"id": ecosystem.id, "code": ecosystem.code, "name": ecosystem.name},
        "creative": None
        if creative is None
        else {
            "id": creative.id,
            "slug": creative.slug,
            "name": creative.name,
            "status": creative.status,
            "holdout": creative.holdout,
        },
    }


def _dna(session: Session, account_id: str | None) -> dict[str, Any] | None:
    if not account_id:
        return None
    account = session.get(Account, account_id)
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
        "observations": [_observation(row) for row in observations],
    }


def _observation(row: AccountDnaObservation) -> dict[str, Any]:
    return {
        "field_name": row.field_name,
        "value": row.value,
        "evidence_kind": row.evidence_kind,
        "confidence": None if row.confidence is None else str(row.confidence),
        "sample_size": row.sample_size,
        "date_start": row.date_start,
        "date_end": row.date_end,
        "source_path": row.source_path,
        "notes": row.notes,
    }


def _genome(
    session: Session, creative: Creative | None, lock: StoryLockVersion | None
) -> tuple[dict[str, Any] | None, str]:
    if creative is None or not creative.current_genome_id:
        return None, "NONE"
    genome = session.get(CreativeGenome, creative.current_genome_id)
    if genome is None:
        return None, "NONE"
    if lock is None or genome.source_story_lock_version_id != lock.id or genome.approval_state != "APPROVED":
        return None, "GENOME_PENDING_FOR_CURRENT_LOCK"
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
            {
                "dimension": row.dimension,
                "value": row.value,
                "assignment": row.assignment,
                "confidence": None if row.confidence is None else str(row.confidence),
                "source": row.source,
            }
            for row in facets
        ],
    }, "BOUND"


def _selected_concept(session: Session, creative: Creative | None) -> dict[str, Any] | None:
    if creative is None or not creative.selected_concept_id:
        return None
    concept = session.get(ConceptCandidate, creative.selected_concept_id)
    if concept is None:
        return None
    return {
        "id": concept.id,
        "task_id": concept.task_id,
        "title": concept.title,
        "premise": concept.premise,
        "family": concept.family,
        "hook_direction": concept.hook_direction,
        "commerce_relation": concept.commerce_relation,
        "status": concept.status,
        "structured_payload": concept.structured_payload,
        "reason_included": "creative.selected_concept_id",
    }


def _benchmarks(
    session: Session, scope: ContextScope, budget: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    account = session.get(Account, scope.account_id) if scope.account_id else None
    ecosystem = session.get(Ecosystem, scope.ecosystem_id) if scope.ecosystem_id else None
    account_name = account.name if account else None
    ecosystem_code = ecosystem.code if ecosystem else None
    rows = session.scalars(
        select(BenchmarkCreative).order_by(BenchmarkCreative.name, BenchmarkCreative.id)
    ).all()
    ranked: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    excluded: list[dict[str, Any]] = []
    for row in rows:
        if row.holdout:
            excluded.append(
                {
                    "holdout": True,
                    "authority": "reference example",
                    "reason_excluded": "holdout benchmark",
                    "reason_included": "withheld from provider context",
                }
            )
            continue
        if ecosystem_code and row.ecosystem_code not in {None, ecosystem_code}:
            excluded.append(
                {**_benchmark_item(row, "different ecosystem"), "reason_excluded": "different ecosystem"}
            )
            continue
        key = _benchmark_key(row, account_name, ecosystem_code)
        reason = _benchmark_reason(row, account_name, ecosystem_code)
        ranked.append((key, _benchmark_item(row, reason)))
    ranked.sort(key=lambda pair: pair[0])
    included = [item for _key, item in ranked[: max(budget, 0)]]
    for _key, item in ranked[max(budget, 0) :]:
        excluded.append({**item, "reason_excluded": "heuristic token budget"})
    return included, excluded


def _benchmark_key(
    row: BenchmarkCreative, account_name: str | None, ecosystem_code: str | None
) -> tuple[Any, ...]:
    account_match = (
        0 if account_name and row.account_name and row.account_name.casefold() == account_name.casefold() else 1
    )
    if ecosystem_code and row.ecosystem_code == ecosystem_code:
        ecosystem_match = 0
    elif row.ecosystem_code is None:
        ecosystem_match = 1
    else:
        ecosystem_match = 2
    return (account_match, ecosystem_match, CATEGORY_RANK.get(row.category or "", 3), row.name, row.id)


def _benchmark_reason(row: BenchmarkCreative, account_name: str | None, ecosystem_code: str | None) -> str:
    reasons: list[str] = []
    if account_name and row.account_name and row.account_name.casefold() == account_name.casefold():
        reasons.append("account match")
    if ecosystem_code and row.ecosystem_code == ecosystem_code:
        reasons.append("ecosystem match")
    if row.category:
        reasons.append(f"category {row.category}")
    if not reasons:
        reasons.append("non-holdout program benchmark")
    return "; ".join(reasons)


def _benchmark_item(row: BenchmarkCreative, reason: str) -> dict[str, Any]:
    return {
        "name": row.name,
        "account": row.account_name,
        "category": row.category,
        "ecosystem": row.ecosystem_code,
        "views": row.views,
        "likes": row.likes,
        "comments": row.comments,
        "shares": row.shares,
        "saves": row.saves,
        "lesson": row.lesson,
        "metrics_note": row.metrics_note,
        "source": row.source_path,
        "holdout": row.holdout,
        "scope": "PROGRAM",
        "reason_included": reason,
        "version": row.id,
        "authority": "reference example",
    }


def _references(
    session: Session,
    scope: ContextScope,
    creative: Creative | None,
    stage: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rows = session.scalars(select(ReferenceBank).order_by(ReferenceBank.name)).all()
    if stage not in PRODUCTION_STAGES:
        excluded = [
            {
                "name": row.name,
                "version": row.id,
                "reason_excluded": f"visual references are not loaded for stage {stage}",
            }
            for row in rows
        ]
        return [], [], excluded
    included = []
    for row in rows:
        if scope.ecosystem_id and row.ecosystem_id not in {None, scope.ecosystem_id}:
            continue
        included.append(
            {
                "name": row.name,
                "source": row.original_path,
                "scope": "PROGRAM",
                "reason_included": "production stage reference metadata",
                "version": row.id,
                "authority": "reference",
            }
        )
    assets: list[dict[str, Any]] = []
    if creative is not None:
        asset_rows = session.scalars(
            select(Asset).where(Asset.creative_id == creative.id).order_by(Asset.name)
        ).all()
        for asset in asset_rows:
            assets.append(
                {
                    "name": asset.name,
                    "role": asset.role,
                    "rights_status": asset.rights_status,
                    "staleness_state": asset.staleness_state,
                    "product_model": asset.product_model,
                    "width": asset.width,
                    "height": asset.height,
                    "original_path": asset.original_path,
                    "story_key": asset.story_key,
                    "reason_included": "creative asset metadata for production context",
                    "version": asset.id,
                }
            )
    return included, assets, []


def _doors(
    session: Session, lock: StoryLockVersion | None, document: StoryLockDocument | None
) -> list[dict[str, Any]]:
    doors: list[dict[str, Any]] = []
    if document is not None:
        for door in document.comment_doors:
            doors.append(
                {
                    "kind": door.kind,
                    "text": door.text,
                    "source": "story lock document",
                    "scope": "CREATIVE",
                    "reason_included": "comment door stored on the current story lock",
                    "version": None if lock is None else lock.id,
                    "authority": "approved story lock",
                }
            )
    if lock is None:
        return doors
    rows = session.scalars(
        select(CommentDoor)
        .where(CommentDoor.story_lock_version_id == lock.id)
        .order_by(CommentDoor.kind, CommentDoor.text)
    ).all()
    seen = {(door["kind"], door["text"]) for door in doors}
    for row in rows:
        if (row.kind, row.text) in seen:
            continue
        doors.append(
            {
                "kind": row.kind,
                "text": row.text,
                "source": "comment_doors",
                "scope": "CREATIVE",
                "reason_included": "doors projected from the current story lock",
                "version": lock.id,
                "authority": "approved story lock",
            }
        )
    return doors
