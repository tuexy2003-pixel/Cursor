from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from creative_os.api.deps import get_session
from creative_os.config import get_settings
from creative_os.importers.handoff import import_handoff
from creative_os.models import (
    Account,
    AccountDnaObservation,
    AccountDnaProfile,
    ApprovalEvent,
    Asset,
    BenchmarkCreative,
    Campaign,
    Comment,
    CommentCluster,
    CommentClusterMember,
    CommentDoor,
    CommentDoorMapping,
    ConceptBatch,
    ContextBundle,
    Creative,
    CreativeGenome,
    Experiment,
    ExperimentVariant,
    ExperimentVariantPost,
    GenomeFacet,
    ManualEvaluation,
    ModelProvider,
    ModelRun,
    PerformanceSnapshot,
    PolicyRule,
    Post,
    PostAsset,
    Program,
    ReferenceBank,
    RegressionTest,
    SkillArtifact,
    SkillVersion,
    SourceArtifact,
    StaleArtifactRecord,
    StoryAuditRecord,
    StoryLineItem,
    StoryLock,
    StoryLockVersion,
    ValidationResult,
    ValidationRun,
)
from creative_os.providers.reasoning import (
    ALLOWED_OUTPUTS,
    DISABLED_CAPABILITIES,
    CreativeReasoningProvider,
    configured_reasoning_providers,
    reasoning_provider,
)
from creative_os.providers.stub import StubProvider
from creative_os.schemas.story_lock import (
    StoryLockCorrection,
    StoryLockDecision,
    StoryLockDocument,
    StoryLockProposal,
)
from creative_os.services.consistency import (
    ConsistencyError,
    resolve_post_attribution,
    validate_cluster_comments,
    validate_door_mapping,
    validate_post,
)
from creative_os.services.context_bundles import create_context_bundle
from creative_os.services.context_compiler import compile_context
from creative_os.services.diff import deep_diff
from creative_os.services.experiments import validate_experiment_isolation
from creative_os.services.mechanics import mechanic_report
from creative_os.services.provider_packet import packet_document
from creative_os.services.story_lock_render import render_canonical_markdown
from creative_os.services.story_locks import (
    StoryLockDecisionError,
    apply_story_lock_correction,
    decide_story_lock_version,
    propose_story_lock_change,
    version_belongs_to_creative,
)
from creative_os.services.tasks import create_creative_task
from creative_os.services.text_reasoning import (
    ReasoningBoundaryError,
    compare_providers,
    execute_text_reasoning,
)
from creative_os.services.validate_creative import validate_creative
from creative_os.util import post_age_hours, utcnow
from creative_os.validation.regression import run_regression_case

router = APIRouter()


class ExperimentIn(BaseModel):
    name: str
    hypothesis: str
    variable_dimension: str
    account_id: str | None = None
    campaign_id: str | None = None
    creative_id: str | None = None
    fixed_notes: str | None = None
    primary_metric: str | None = None
    control_name: str = "control"
    variant_name: str = "variant"
    control_changes: dict[str, str] = Field(default_factory=dict)
    variant_changes: dict[str, str] = Field(default_factory=dict)
    mode: str = "SINGLE_VARIABLE"


class PostAssetIn(BaseModel):
    asset_id: str
    slide_index: int | None = None
    role: str | None = None
    sort_order: int | None = None


class PostIn(BaseModel):
    platform: str = "tiktok"
    creative_id: str | None = None
    account_id: str | None = None
    campaign_id: str | None = None
    url: str | None = None
    notes: str | None = None
    external_id: str | None = None
    published_at: datetime | None = None
    story_lock_version_id: str | None = None
    creative_genome_id: str | None = None
    experiment_variant_id: str | None = None
    attribution_mode: str = "CURRENT_PUBLISH"
    assets: list[PostAssetIn] = Field(default_factory=list)


class ContextBundleIn(BaseModel):
    stage: str = "STORY_DEVELOPMENT"
    as_of: datetime | None = None
    heuristic_budget: int = 24
    instruction: str | None = None
    expected_output_type: str | None = None


class SnapshotIn(BaseModel):
    source: str
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    saves: int | None = None
    profile_visits: int | None = None
    link_clicks: int | None = None
    conversions: int | None = None
    revenue: str | None = None
    revenue_amount: str | None = None
    revenue_currency: str | None = None
    measurement_window: str | None = None
    raw_payload: dict[str, str] | None = None


class CommentIn(BaseModel):
    body: str
    stance: str | None = None
    source: str | None = None


class ClusterIn(BaseModel):
    label: str
    size: int
    example_comments: list[str] = Field(default_factory=list)
    unexpected: bool = False
    door_id: str | None = None
    relationship: str = "unmatched"
    comment_ids: list[str] = Field(default_factory=list)
    assigned_by: str | None = None


def session_dep(session: Session = Depends(get_session)) -> Session:
    return session


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "creative-os"}


@router.get("/summary")
def summary(session: Session = Depends(session_dep)) -> dict[str, int]:
    tables = {
        "programs": Program,
        "accounts": Account,
        "campaigns": Campaign,
        "creatives": Creative,
        "story_lock_versions": StoryLockVersion,
        "skills": SkillArtifact,
        "skill_versions": SkillVersion,
        "policy_rules": PolicyRule,
        "assets": Asset,
        "regression_tests": RegressionTest,
        "benchmarks": BenchmarkCreative,
        "source_artifacts": SourceArtifact,
    }
    return {
        name: session.scalar(select(func.count()).select_from(model)) or 0 for name, model in tables.items()
    }


@router.post("/import/handoff")
def run_import(session: Session = Depends(session_dep)) -> dict[str, object]:
    settings = get_settings()
    report = import_handoff(session, settings.resolved_snapshot_root())
    return report.as_dict()


@router.get("/programs")
def programs(session: Session = Depends(session_dep)) -> list[dict[str, str | None]]:
    rows = session.scalars(select(Program).order_by(Program.name)).all()
    return [{"id": row.id, "slug": row.slug, "name": row.name, "description": row.description} for row in rows]


@router.get("/accounts")
def accounts(session: Session = Depends(session_dep)) -> list[dict[str, Any]]:
    rows = session.scalars(select(Account).order_by(Account.name)).all()
    payload: list[dict[str, Any]] = []
    for row in rows:
        profile = None
        if row.current_approved_dna_profile_id:
            profile = session.get(AccountDnaProfile, row.current_approved_dna_profile_id)
            if profile is not None and profile.approval_state != "APPROVED":
                profile = None
        observations: list[dict[str, Any]] = []
        if profile:
            observations = [
                {
                    "field_name": item.field_name,
                    "value": item.value,
                    "evidence_kind": item.evidence_kind,
                    "sample_size": item.sample_size,
                    "notes": item.notes,
                }
                for item in session.scalars(
                    select(AccountDnaObservation).where(AccountDnaObservation.profile_id == profile.id)
                ).all()
            ]
        payload.append(
            {
                "id": row.id,
                "name": row.name,
                "slug": row.slug,
                "notes": row.notes,
                "dna": observations,
            }
        )
    return payload


@router.get("/campaigns")
def campaigns(session: Session = Depends(session_dep)) -> list[dict[str, str | None]]:
    rows = session.scalars(select(Campaign).order_by(Campaign.name)).all()
    return [{"id": row.id, "name": row.name, "slug": row.slug, "notes": row.notes} for row in rows]


@router.get("/creatives")
def creatives(session: Session = Depends(session_dep)) -> list[dict[str, object]]:
    rows = session.scalars(select(Creative).order_by(Creative.name)).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "slug": row.slug,
            "status": row.status,
            "holdout": row.holdout,
            "current_story_lock_version_id": row.current_approved_story_lock_version_id,
        }
        for row in rows
    ]


@router.get("/creatives/{creative_id}")
def creative_detail(creative_id: str, session: Session = Depends(session_dep)) -> dict[str, object]:
    creative = session.get(Creative, creative_id)
    if creative is None:
        raise HTTPException(status_code=404, detail="creative not found")
    lock = session.scalar(select(StoryLock).where(StoryLock.creative_id == creative.id))
    versions: list[StoryLockVersion] = []
    if lock:
        versions = list(
            session.scalars(
                select(StoryLockVersion)
                .where(StoryLockVersion.story_lock_id == lock.id)
                .order_by(StoryLockVersion.version_number)
            ).all()
        )
    current = None
    if creative.current_approved_story_lock_version_id:
        current = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    items: list[StoryLineItem] = []
    doors: list[CommentDoor] = []
    if current:
        items = list(
            session.scalars(
                select(StoryLineItem)
                .where(StoryLineItem.story_lock_version_id == current.id)
                .order_by(StoryLineItem.position)
            ).all()
        )
        doors = list(
            session.scalars(select(CommentDoor).where(CommentDoor.story_lock_version_id == current.id)).all()
        )
    assets = session.scalars(select(Asset).where(Asset.creative_id == creative.id)).all()
    approvals: list[ApprovalEvent] = []
    if lock:
        approvals = list(
            session.scalars(
                select(ApprovalEvent)
                .where(ApprovalEvent.object_id == lock.id)
                .order_by(ApprovalEvent.created_at)
            ).all()
        )
    genome_facets = _facets(session, creative.id)
    previous = None
    if current is not None and current.supersedes_version_id:
        previous = session.get(StoryLockVersion, current.supersedes_version_id)
    diff_from_previous = (
        deep_diff(previous.content_json, current.content_json)
        if current is not None and previous is not None
        else None
    )
    return {
        "id": creative.id,
        "name": creative.name,
        "slug": creative.slug,
        "status": creative.status,
        "holdout": creative.holdout,
        "notes": creative.notes,
        "current_story_lock_version_id": creative.current_approved_story_lock_version_id,
        "story_lock": None
        if current is None
        else {
            "version_number": current.version_number,
            "approved_by": current.approved_by,
            "change_reason": current.change_reason,
            "content": current.content_json,
        },
        "versions": [
            {
                "id": version.id,
                "version_number": version.version_number,
                "supersedes_version_id": version.supersedes_version_id,
                "change_reason": version.change_reason,
                "approved_by": version.approved_by,
                "content_hash": version.content_hash,
            }
            for version in versions
        ],
        "line_items": [
            {
                "position": item.position,
                "title": item.title,
                "unit_price": item.unit_price,
                "model": item.model,
            }
            for item in items
        ],
        "comment_doors": [{"id": door.id, "kind": door.kind, "text": door.text} for door in doors],
        "assets": [
            {
                "id": asset.id,
                "name": asset.name,
                "role": asset.role,
                "rights_status": asset.rights_status,
                "stale": asset.stale,
                "staleness_state": asset.staleness_state,
                "original_path": asset.original_path,
                "present_in_snapshot": asset.present_in_snapshot,
                "product_model": asset.product_model,
            }
            for asset in assets
        ],
        "approvals": [
            {
                "id": event.id,
                "status": event.status,
                "actor": event.actor,
                "notes": event.notes,
                "version_id": event.version_id,
            }
            for event in approvals
        ],
        "genome": genome_facets,
        "diff_from_previous": diff_from_previous,
        "context_preview": compile_context(session, creative, stage="full"),
    }


def _decision_http(exc: StoryLockDecisionError) -> HTTPException:
    status = 409 if exc.code in {"OUTDATED_PROPOSAL", "STALE_PRECONDITION"} else 400
    return HTTPException(status_code=status, detail=f"{exc.code}: {exc}")


def _lock_version(session: Session, creative_id: str, token: str) -> StoryLockVersion | None:
    found = session.get(StoryLockVersion, token)
    if found is not None:
        if not version_belongs_to_creative(session, creative_id, found):
            raise StoryLockDecisionError(
                "CROSS_CREATIVE",
                "story lock version does not belong to this creative",
            )
        return found
    if not token.isdigit():
        return None
    lock = session.scalar(select(StoryLock).where(StoryLock.creative_id == creative_id))
    if lock is None:
        return None
    return session.scalar(
        select(StoryLockVersion).where(
            StoryLockVersion.story_lock_id == lock.id,
            StoryLockVersion.version_number == int(token),
        )
    )


def _facets(session: Session, creative_id: str) -> list[dict[str, object]]:
    creative = session.get(Creative, creative_id)
    genome = None
    if creative and creative.current_genome_id:
        genome = session.get(CreativeGenome, creative.current_genome_id)
    if genome is None:
        return []
    rows = session.scalars(select(GenomeFacet).where(GenomeFacet.genome_id == genome.id)).all()
    return [
        {
            "dimension": row.dimension,
            "value": row.value,
            "assignment": row.assignment,
            "source": row.source,
            "confidence": None if row.confidence is None else float(row.confidence),
        }
        for row in rows
    ]


@router.get("/creatives/{creative_id}/story-lock.md")
def export_lock(creative_id: str, session: Session = Depends(session_dep)) -> dict[str, str]:
    creative = _creative_or_404(session, creative_id)
    version = _current_version(session, creative)
    document = StoryLockDocument.model_validate(version.content_json)
    return {"markdown": render_canonical_markdown(document), "version_id": version.id}


@router.get("/creatives/{creative_id}/story-lock/diff")
def lock_diff(
    creative_id: str,
    left: str,
    right: str,
    session: Session = Depends(session_dep),
) -> dict[str, object]:
    _creative_or_404(session, creative_id)
    try:
        older = _lock_version(session, creative_id, left)
        newer = _lock_version(session, creative_id, right)
    except StoryLockDecisionError as exc:
        raise _decision_http(exc) from exc
    if older is None or newer is None:
        raise HTTPException(status_code=404, detail="story lock version not found")
    return {"paths": deep_diff(older.content_json, newer.content_json)}


@router.post("/creatives/{creative_id}/story-lock/corrections")
def correct_lock(
    creative_id: str,
    body: StoryLockCorrection,
    session: Session = Depends(session_dep),
) -> dict[str, object]:
    creative = _creative_or_404(session, creative_id)
    operator = get_settings().operator_identity
    try:
        version = apply_story_lock_correction(
            session,
            creative,
            body.changes,
            operator,
            body.reason,
            patches=body.patches,
            expected_current_story_lock_version_id=body.expected_current_story_lock_version_id,
        )
    except StoryLockDecisionError as exc:
        raise _decision_http(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "version_id": version.id,
        "version_number": version.version_number,
        "supersedes_version_id": version.supersedes_version_id,
        "content_hash": version.content_hash,
        "document_hash": version.document_hash,
        "approved_by": operator,
    }


@router.post("/creatives/{creative_id}/story-lock/proposals")
def propose_lock(
    creative_id: str,
    body: StoryLockProposal,
    session: Session = Depends(session_dep),
) -> dict[str, object]:
    creative = _creative_or_404(session, creative_id)
    try:
        version = propose_story_lock_change(
            session,
            creative,
            body.changes,
            body.proposer,
            body.reason,
            patches=body.patches,
            expected_current_story_lock_version_id=body.expected_current_story_lock_version_id,
        )
    except StoryLockDecisionError as exc:
        raise _decision_http(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "version_id": version.id,
        "version_number": version.version_number,
        "approval_state": version.approval_state,
        "current_approved_story_lock_version_id": creative.current_approved_story_lock_version_id,
    }


@router.post("/creatives/{creative_id}/story-lock/versions/{version_id}/decision")
def decide_lock(
    creative_id: str,
    version_id: str,
    body: StoryLockDecision,
    session: Session = Depends(session_dep),
) -> dict[str, object]:
    creative = _creative_or_404(session, creative_id)
    try:
        version = _lock_version(session, creative_id, version_id)
    except StoryLockDecisionError as exc:
        raise _decision_http(exc) from exc
    if version is None:
        raise HTTPException(status_code=404, detail="story lock version not found")
    operator = get_settings().operator_identity
    try:
        decide_story_lock_version(session, creative, version, body.decision, operator, body.notes)
    except StoryLockDecisionError as exc:
        raise _decision_http(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "version_id": version.id,
        "decision": body.decision,
        "actor": operator,
        "current_approved_story_lock_version_id": creative.current_approved_story_lock_version_id,
    }


@router.get("/creatives/{creative_id}/context-preview")
def context_preview(
    creative_id: str,
    stage: str = "full",
    heuristic_budget: int = 24,
    session: Session = Depends(session_dep),
) -> dict[str, object]:
    creative = _creative_or_404(session, creative_id)
    try:
        return compile_context(session, creative, stage=stage, heuristic_budget=heuristic_budget)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/creatives/{creative_id}/context-bundles")
def compile_bundle(
    creative_id: str,
    body: ContextBundleIn,
    session: Session = Depends(session_dep),
) -> dict[str, object]:
    creative = _creative_or_404(session, creative_id)
    try:
        task = create_creative_task(
            session,
            program_id=creative.program_id,
            account_id=creative.account_id,
            campaign_id=creative.campaign_id,
            creative_id=creative.id,
            ecosystem_id=creative.ecosystem_id,
            stage=body.stage,
            instruction=body.instruction or f"Compile {body.stage} context for {creative.slug}.",
            created_by=get_settings().operator_identity,
            expected_output_type=body.expected_output_type,
        )
        bundle = create_context_bundle(
            session,
            creative,
            stage=body.stage,
            as_of=body.as_of,
            heuristic_budget=body.heuristic_budget,
            task=task,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _bundle_view(bundle)


@router.get("/context-bundles/{bundle_id}/packet")
def export_bundle_packet(
    bundle_id: str,
    format: str = "markdown",
    session: Session = Depends(session_dep),
) -> object:
    bundle = session.get(ContextBundle, bundle_id)
    if bundle is None:
        raise HTTPException(status_code=404, detail="context bundle not found")
    if format == "json":
        return packet_document(bundle)
    if format == "markdown":
        return PlainTextResponse(bundle.compiled_text)
    raise HTTPException(status_code=400, detail="format must be markdown or json")


@router.get("/creatives/{creative_id}/context-bundles/{bundle_id}")
def read_bundle(creative_id: str, bundle_id: str, session: Session = Depends(session_dep)) -> dict[str, object]:
    _creative_or_404(session, creative_id)
    bundle = session.get(ContextBundle, bundle_id)
    if bundle is None or bundle.creative_id != creative_id:
        raise HTTPException(status_code=404, detail="context bundle not found")
    return _bundle_view(bundle)


def _bundle_view(bundle: ContextBundle) -> dict[str, object]:
    payload = bundle.compiled_payload
    return {
        "id": bundle.id,
        "payload_hash": bundle.payload_hash,
        "compiler_version": bundle.compiler_version,
        "status": bundle.status,
        "requested_stage": bundle.requested_stage,
        "as_of": bundle.as_of.isoformat(),
        "creative_id": bundle.creative_id,
        "account_id": bundle.account_id,
        "campaign_id": bundle.campaign_id,
        "story_lock_version_id": bundle.story_lock_version_id,
        "account_dna_profile_id": bundle.account_dna_profile_id,
        "creative_genome_id": bundle.creative_genome_id,
        "size_estimate": bundle.size_estimate,
        "token_estimate": bundle.token_estimate,
        "creative_task_id": bundle.creative_task_id,
        "task": payload.get("task"),
        "genome_state": payload.get("genome_state"),
        "section_sizes": payload.get("section_sizes"),
        "story_lock_floating_hook": (
            ((payload.get("current_story_lock_version") or {}).get("document") or {}).get("floating_hook")
        ),
        "output_contract": (payload.get("output_contract") or {}).get("name"),
        "provider_execution": "NOT_IMPLEMENTED",
        "global_invariants": payload.get("global_invariants", []),
        "program_policies": payload.get("program_policies", []),
        "account_policies": payload.get("account_policies", []),
        "campaign_policies": payload.get("campaign_policies", []),
        "creative_locks": payload.get("creative_locks", []),
        "skill_versions": payload.get("skill_versions", []),
        "benchmarks": payload.get("benchmarks", []),
        "comment_doors": payload.get("comment_doors", []),
        "continuity": payload.get("continuity", []),
        "mechanic_context": payload.get("mechanic_context"),
        "references": payload.get("references", []),
        "excluded_for_token_budget": payload.get("excluded_for_token_budget", []),
        "compiled_text": bundle.compiled_text,
    }


@router.post("/creatives/{creative_id}/validation")
def validate(creative_id: str, session: Session = Depends(session_dep)) -> dict[str, object]:
    creative = _creative_or_404(session, creative_id)
    findings = validate_creative(session, creative)
    run = ValidationRun(subject_type="creative", subject_id=creative.id, created_at=utcnow())
    session.add(run)
    session.flush()
    for code, status, message in findings:
        session.add(
            ValidationResult(
                run_id=run.id,
                check_code=code,
                status=status,
                message=message,
                details={},
            )
        )
    return {
        "run_id": run.id,
        "results": [
            {"check": code, "status": status, "message": message} for code, status, message in findings
        ],
    }


@router.get("/assets")
def assets(session: Session = Depends(session_dep)) -> list[dict[str, object]]:
    rows = session.scalars(select(Asset).order_by(Asset.name)).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "role": row.role,
            "rights_status": row.rights_status,
            "stale": row.stale,
            "original_path": row.original_path,
            "present_in_snapshot": row.present_in_snapshot,
            "story_key": row.story_key,
            "ecosystem_code": row.ecosystem_code,
        }
        for row in rows
    ]


@router.get("/assets/{asset_id}/stale")
def asset_stale(asset_id: str, session: Session = Depends(session_dep)) -> list[dict[str, str | None]]:
    rows = session.scalars(select(StaleArtifactRecord).where(StaleArtifactRecord.asset_id == asset_id)).all()
    return [
        {"id": row.id, "reason": row.reason, "story_lock_version_id": row.story_lock_version_id} for row in rows
    ]


@router.get("/references")
def references(session: Session = Depends(session_dep)) -> list[dict[str, str | None]]:
    rows = session.scalars(select(ReferenceBank).order_by(ReferenceBank.name)).all()
    return [
        {"id": row.id, "name": row.name, "original_path": row.original_path, "notes": row.notes} for row in rows
    ]


@router.get("/policies")
def policies(session: Session = Depends(session_dep)) -> dict[str, object]:
    skills = session.scalars(select(SkillArtifact).order_by(SkillArtifact.slug)).all()
    skill_rows = []
    for skill in skills:
        versions = session.scalars(
            select(SkillVersion).where(SkillVersion.skill_id == skill.id).order_by(SkillVersion.created_at)
        ).all()
        skill_rows.append(
            {
                "slug": skill.slug,
                "name": skill.name,
                "current_version_id": skill.current_version_id,
                "versions": [
                    {
                        "id": version.id,
                        "version_label": version.version_label,
                        "status": version.status,
                        "scope_level": version.scope_level,
                        "content_hash": version.content_hash,
                        "source_path": version.source_path,
                        "is_current": version.id == skill.current_version_id,
                    }
                    for version in versions
                ],
            }
        )
    rules = session.scalars(select(PolicyRule).order_by(PolicyRule.code)).all()
    return {
        "skills": skill_rows,
        "rules": [
            {
                "code": rule.code,
                "scope_level": rule.scope_level,
                "rule_kind": rule.rule_kind,
                "title": rule.title,
                "status": rule.status,
                "scope_id": rule.scope_id,
                "source_path": rule.source_path,
            }
            for rule in rules
        ],
    }


@router.get("/policies/skills/{slug}")
def skill_body(slug: str, session: Session = Depends(session_dep)) -> dict[str, str]:
    skill = session.scalar(select(SkillArtifact).where(SkillArtifact.slug == slug))
    if skill is None:
        raise HTTPException(status_code=404, detail="skill not found")
    version = None
    if skill.current_version_id:
        version = session.get(SkillVersion, skill.current_version_id)
    if version is None:
        version = session.scalar(
            select(SkillVersion)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.version_label == "handoff-2026-10-05")
            .order_by(SkillVersion.created_at)
        )
    if version is None:
        raise HTTPException(status_code=404, detail="skill version not found")
    return {
        "slug": slug,
        "status": version.status,
        "version_label": version.version_label,
        "approval_state": version.approval_state,
        "content": version.content,
        "content_hash": version.content_hash,
    }


@router.get("/benchmarks")
def benchmarks(session: Session = Depends(session_dep)) -> list[dict[str, object]]:
    rows = session.scalars(select(BenchmarkCreative).order_by(BenchmarkCreative.name)).all()
    return [
        {
            "name": row.name,
            "account_name": row.account_name,
            "category": row.category,
            "views": row.views,
            "holdout": row.holdout,
            "metrics_note": row.metrics_note,
        }
        for row in rows
    ]


@router.get("/regression-tests")
def regression_tests(session: Session = Depends(session_dep)) -> list[dict[str, str]]:
    rows = session.scalars(select(RegressionTest).order_by(RegressionTest.code)).all()
    return [
        {
            "code": row.code,
            "category": row.category,
            "evaluation_mode": row.evaluation_mode,
            "expected_decision": row.expected_decision,
            "input": row.input_text,
        }
        for row in rows
    ]


@router.post("/regression-tests/run")
def run_regressions(session: Session = Depends(session_dep)) -> dict[str, object]:
    rows = session.scalars(select(RegressionTest).order_by(RegressionTest.code)).all()
    results = []
    for row in rows:
        status, message = run_regression_case(row.code)
        results.append(
            {
                "code": row.code,
                "evaluation_mode": row.evaluation_mode,
                "status": status,
                "message": message,
            }
        )
    return {"results": results}


@router.get("/experiments")
def experiments(session: Session = Depends(session_dep)) -> list[dict[str, Any]]:
    rows = session.scalars(select(Experiment).order_by(Experiment.created_at.desc())).all()
    payload: list[dict[str, Any]] = []
    for row in rows:
        variants = session.scalars(
            select(ExperimentVariant).where(ExperimentVariant.experiment_id == row.id)
        ).all()
        payload.append(
            {
                "id": row.id,
                "name": row.name,
                "hypothesis": row.hypothesis,
                "variable_dimension": row.variable_dimension,
                "status": row.status,
                "primary_metric": row.primary_metric,
                "variants": [
                    {
                        "name": variant.name,
                        "is_control": variant.is_control,
                        "changes": variant.changes,
                    }
                    for variant in variants
                ],
            }
        )
    return payload


@router.post("/experiments")
def create_experiment(body: ExperimentIn, session: Session = Depends(session_dep)) -> dict[str, str]:
    try:
        changed = validate_experiment_isolation(
            mode=body.mode,
            variable_dimension=body.variable_dimension,
            control=dict(body.control_changes),
            variant=dict(body.variant_changes),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    experiment = Experiment(
        name=body.name,
        hypothesis=body.hypothesis,
        account_id=body.account_id,
        campaign_id=body.campaign_id,
        creative_id=body.creative_id,
        variable_dimension=body.variable_dimension,
        mode=body.mode,
        changed_dimensions=changed,
        fixed_notes=body.fixed_notes,
        primary_metric=body.primary_metric,
        secondary_metrics=[],
        status="draft",
        created_at=utcnow(),
    )
    session.add(experiment)
    session.flush()
    session.add(
        ExperimentVariant(
            experiment_id=experiment.id,
            name=body.control_name,
            is_control=True,
            changes=body.control_changes,
            fixed={"dimension": body.variable_dimension},
        )
    )
    session.add(
        ExperimentVariant(
            experiment_id=experiment.id,
            name=body.variant_name,
            is_control=False,
            changes=body.variant_changes,
            fixed={"dimension": body.variable_dimension},
        )
    )
    return {"id": experiment.id}


@router.get("/posts")
def posts(session: Session = Depends(session_dep)) -> list[dict[str, Any]]:
    rows = session.scalars(select(Post).order_by(Post.created_at.desc())).all()
    payload: list[dict[str, Any]] = []
    for row in rows:
        snapshots = session.scalars(
            select(PerformanceSnapshot).where(PerformanceSnapshot.post_id == row.id)
        ).all()
        payload.append(
            {
                "id": row.id,
                "platform": row.platform,
                "url": row.url,
                "notes": row.notes,
                "snapshots": [
                    {
                        "source": snap.source,
                        "views": snap.views,
                        "likes": snap.likes,
                        "comments": snap.comments,
                        "captured_at": snap.captured_at.isoformat(),
                    }
                    for snap in snapshots
                ],
            }
        )
    return payload


@router.post("/posts")
def create_post(body: PostIn, session: Session = Depends(session_dep)) -> dict[str, str]:
    creative = session.get(Creative, body.creative_id) if body.creative_id else None
    if body.creative_id and creative is None:
        raise HTTPException(status_code=400, detail="creative was not found")
    account = session.get(Account, body.account_id) if body.account_id else None
    if body.account_id and account is None:
        raise HTTPException(status_code=400, detail="account was not found")
    campaign = session.get(Campaign, body.campaign_id) if body.campaign_id else None
    if body.campaign_id and campaign is None:
        raise HTTPException(status_code=400, detail="campaign was not found")
    lock_id = body.story_lock_version_id
    if lock_id is None and creative is not None:
        lock_id = creative.current_approved_story_lock_version_id
    story_lock = session.get(StoryLockVersion, lock_id) if lock_id else None
    variant = session.get(ExperimentVariant, body.experiment_variant_id) if body.experiment_variant_id else None
    if body.experiment_variant_id and variant is None:
        raise HTTPException(status_code=400, detail="experiment variant was not found")
    assets = []
    for spec in body.assets:
        asset = session.get(Asset, spec.asset_id)
        if asset is None:
            raise HTTPException(status_code=400, detail=f"asset {spec.asset_id} was not found")
        assets.append(asset)
    try:
        account_id, campaign_id, genome_id = resolve_post_attribution(
            session,
            creative=creative,
            account_id=body.account_id,
            campaign_id=body.campaign_id,
            story_lock_version_id=lock_id,
            creative_genome_id=body.creative_genome_id,
            assets=assets,
            attribution_mode=body.attribution_mode,
        )
        account = session.get(Account, account_id) if account_id else None
        campaign = session.get(Campaign, campaign_id) if campaign_id else None
        validate_post(
            session,
            creative=creative,
            account=account,
            campaign=campaign,
            story_lock=story_lock,
            variant=variant,
            assets=assets,
        )
    except ConsistencyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    post = Post(
        creative_id=body.creative_id,
        account_id=account_id,
        campaign_id=campaign_id,
        platform=body.platform,
        url=body.url,
        notes=body.notes,
        external_id=body.external_id,
        published_at=body.published_at,
        story_lock_version_id=lock_id,
        creative_genome_id=genome_id,
        experiment_variant_id=body.experiment_variant_id,
        created_at=utcnow(),
    )
    session.add(post)
    session.flush()
    for spec, asset in zip(body.assets, assets, strict=True):
        session.add(
            PostAsset(
                post_id=post.id,
                asset_id=asset.id,
                slide_index=spec.slide_index,
                sort_order=spec.sort_order,
                role=spec.role or asset.role,
            )
        )
    if variant is not None:
        session.add(ExperimentVariantPost(variant_id=variant.id, post_id=post.id, created_at=utcnow()))
    return {"id": post.id, "story_lock_version_id": lock_id or ""}


@router.post("/posts/{post_id}/snapshots")
def add_snapshot(post_id: str, body: SnapshotIn, session: Session = Depends(session_dep)) -> dict[str, str]:
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    captured_at = utcnow()
    age = None
    if post.published_at is not None:
        age = post_age_hours(post.published_at, captured_at)
    amount = _money(body.revenue_amount)
    snap = PerformanceSnapshot(
        post_id=post.id,
        source=body.source,
        captured_at=captured_at,
        post_age_hours=age,
        measurement_window=body.measurement_window,
        views=body.views,
        likes=body.likes,
        comments=body.comments,
        shares=body.shares,
        saves=body.saves,
        profile_visits=body.profile_visits,
        link_clicks=body.link_clicks,
        conversions=body.conversions,
        revenue=body.revenue,
        revenue_amount=amount,
        revenue_currency=body.revenue_currency,
        raw_payload=body.raw_payload,
    )
    session.add(snap)
    session.flush()
    return {"id": snap.id}


@router.get("/comments")
def comments(session: Session = Depends(session_dep)) -> dict[str, object]:
    doors = session.scalars(select(CommentDoor)).all()
    clusters = session.scalars(select(CommentCluster)).all()
    mappings = session.scalars(select(CommentDoorMapping)).all()
    return {
        "doors": [
            {"id": door.id, "kind": door.kind, "text": door.text, "creative_id": door.creative_id}
            for door in doors
        ],
        "clusters": [
            {
                "id": cluster.id,
                "label": cluster.label,
                "size": cluster.size,
                "unexpected": cluster.unexpected,
                "examples": cluster.example_comments,
            }
            for cluster in clusters
        ],
        "mappings": [
            {
                "door_id": item.door_id,
                "cluster_id": item.cluster_id,
                "relationship": item.relationship,
            }
            for item in mappings
        ],
    }


@router.post("/posts/{post_id}/comments")
def add_comment(post_id: str, body: CommentIn, session: Session = Depends(session_dep)) -> dict[str, str]:
    if session.get(Post, post_id) is None:
        raise HTTPException(status_code=404, detail="post not found")
    comment = Comment(
        post_id=post_id,
        body=body.body,
        stance=body.stance,
        source=body.source,
        observed_at=None,
        created_at=utcnow(),
    )
    session.add(comment)
    session.flush()
    return {"id": comment.id}


@router.post("/posts/{post_id}/clusters")
def add_cluster(post_id: str, body: ClusterIn, session: Session = Depends(session_dep)) -> dict[str, str]:
    if session.get(Post, post_id) is None:
        raise HTTPException(status_code=404, detail="post not found")
    try:
        comments = validate_cluster_comments(session, post_id, body.comment_ids)
    except ConsistencyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    cluster = CommentCluster(
        post_id=post_id,
        label=body.label,
        size=body.size if not comments else len(comments),
        example_comments=body.example_comments,
        sentiment=None,
        confidence=None,
        unexpected=body.unexpected,
        created_at=utcnow(),
    )
    session.add(cluster)
    session.flush()
    for comment in comments:
        session.add(
            CommentClusterMember(
                cluster_id=cluster.id,
                comment_id=comment.id,
                confidence=None,
                assigned_by=body.assigned_by,
                human_override=False,
                created_at=utcnow(),
            )
        )
    relationship = body.relationship
    if body.door_id is None and body.unexpected:
        relationship = "unexpected"
    door = session.get(CommentDoor, body.door_id) if body.door_id else None
    if body.door_id and door is None:
        raise HTTPException(status_code=400, detail="comment door was not found")
    try:
        validate_door_mapping(session, door, cluster)
    except ConsistencyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    session.add(
        CommentDoorMapping(
            door_id=body.door_id,
            cluster_id=cluster.id,
            relationship=relationship,
            notes=None,
            created_at=utcnow(),
        )
    )
    return {"id": cluster.id}


@router.get("/novelty")
def novelty(account_id: str | None = None, session: Session = Depends(session_dep)) -> dict[str, object]:
    return mechanic_report(session, account_id)


def _money(value: str | None) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise HTTPException(status_code=400, detail="revenue_amount must be a decimal") from exc


class TextRunIn(BaseModel):
    context_bundle_id: str
    provider: str


class CompareRunsIn(BaseModel):
    context_bundle_id: str
    providers: list[str] = Field(min_length=1)


@router.get("/runs")
def runs(session: Session = Depends(session_dep)) -> dict[str, object]:
    providers = session.scalars(select(ModelProvider)).all()
    model_runs = session.scalars(select(ModelRun).order_by(ModelRun.started_at.desc())).all()
    validation_runs = session.scalars(select(ValidationRun).order_by(ValidationRun.created_at.desc())).all()
    bundles = session.scalars(select(ContextBundle).order_by(ContextBundle.created_at.desc()).limit(30)).all()
    evaluations = session.scalars(
        select(ManualEvaluation).order_by(ManualEvaluation.run_timestamp.desc())
    ).all()
    return {
        "providers": [
            {
                "name": row.name,
                "capability": row.capability,
                "model_version": row.model_version,
                "notes": row.notes,
            }
            for row in providers
        ],
        "text_reasoning_providers": [
            {
                "name": provider.name,
                "available": provider.available(),
                "status": "READY" if provider.available() else "NOT_IMPLEMENTED",
            }
            for provider in configured_reasoning_providers()
        ],
        "allowed_stages": sorted(ALLOWED_OUTPUTS),
        "disabled_capabilities": sorted(DISABLED_CAPABILITIES),
        "context_bundles": [_bundle_choice(row) for row in bundles],
        "manual_evaluations": [_evaluation_view(row) for row in evaluations],
        "model_runs": [_run_view(session, row) for row in model_runs],
        "validation_runs": [
            {"id": row.id, "subject_type": row.subject_type, "subject_id": row.subject_id}
            for row in validation_runs
        ],
    }


@router.post("/runs/text-reasoning")
def text_reasoning(body: TextRunIn, session: Session = Depends(session_dep)) -> dict[str, object]:
    bundle = _bundle_or_404(session, body.context_bundle_id)
    try:
        provider = reasoning_provider(body.provider)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail="unknown text reasoning provider") from exc
    return {"run": _execute_bundle(session, bundle, provider)}


@router.post("/runs/compare")
def compare_runs(body: CompareRunsIn, session: Session = Depends(session_dep)) -> dict[str, object]:
    bundle = _bundle_or_404(session, body.context_bundle_id)
    providers = []
    for name in body.providers:
        try:
            providers.append(reasoning_provider(name))
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"unknown text reasoning provider: {name}") from exc
    try:
        created = compare_providers(session, bundle, providers)
    except ReasoningBoundaryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "context_bundle_id": bundle.id,
        "context_bundle_hash": bundle.payload_hash,
        "runs": [_run_view(session, row) for row in created],
    }


def _bundle_or_404(session: Session, bundle_id: str) -> ContextBundle:
    bundle = session.get(ContextBundle, bundle_id)
    if bundle is None:
        raise HTTPException(status_code=404, detail="context bundle not found")
    return bundle


def _execute_bundle(
    session: Session, bundle: ContextBundle, provider: CreativeReasoningProvider
) -> dict[str, object]:
    try:
        run = execute_text_reasoning(session, bundle, provider)
    except ReasoningBoundaryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _run_view(session, run)


def _bundle_choice(bundle: ContextBundle) -> dict[str, object]:
    task = (bundle.compiled_payload or {}).get("task") or {}
    instruction = str(task.get("instruction") or "")
    return {
        "id": bundle.id,
        "stage": bundle.requested_stage,
        "payload_hash": bundle.payload_hash,
        "expected_output_type": task.get("expected_output_type"),
        "instruction": instruction[:180],
    }


def _evaluation_view(row: ManualEvaluation) -> dict[str, object]:
    return {
        "id": row.id,
        "origin": row.origin,
        "provider_name": row.provider_name,
        "model_name": row.model_name,
        "packet_hash": row.packet_hash,
        "recorded_context_bundle_id": row.recorded_context_bundle_id,
        "recorded_task_id": row.recorded_task_id,
        "stage": row.stage,
        "rubric_score": row.rubric_score,
        "rubric_item_scores": row.rubric_item_scores,
        "notes": row.notes,
        "run_timestamp": row.run_timestamp.isoformat(),
        "source_path": row.source_path,
    }


def _run_view(session: Session, run: ModelRun) -> dict[str, object]:
    batch = session.scalar(select(ConceptBatch).where(ConceptBatch.source_model_run_id == run.id))
    audit = session.scalar(select(StoryAuditRecord).where(StoryAuditRecord.model_run_id == run.id))
    raw = run.raw_response or ""
    return {
        "id": run.id,
        "capability": run.capability,
        "status": run.status,
        "error": run.error,
        "context_bundle_id": run.context_bundle_id,
        "context_bundle_hash": run.context_bundle_hash,
        "creative_task_id": run.creative_task_id,
        "provider_model_name": run.provider_model_name,
        "provider_model_version": run.provider_model_version,
        "latency_ms": run.latency_ms,
        "input_tokens": run.input_tokens,
        "output_tokens": run.output_tokens,
        "cached_tokens": run.cached_tokens,
        "cost": None if run.cost is None else str(run.cost),
        "cost_currency": run.cost_currency,
        "execution_origin": run.execution_origin,
        "parse_error": run.parse_error,
        "parsed_output": run.parsed_output,
        "parent_run_id": run.parent_run_id,
        "raw_response_excerpt": raw[:500],
        "diversity": None
        if batch is None
        else {"level": batch.diversity_level, "report": batch.diversity_report, "status": batch.status},
        "story_audit": None
        if audit is None
        else {
            "id": audit.id,
            "record_status": audit.record_status,
            "overall_status": audit.overall_status,
            "diagnosis": audit.diagnosis,
        },
    }


@router.post("/runs/stub")
def stub_run(session: Session = Depends(session_dep)) -> dict[str, object]:
    provider = session.scalar(select(ModelProvider).where(ModelProvider.capability == "creative_reasoning"))
    stub = StubProvider(provider.name if provider else "unconfigured", "creative_reasoning")
    result = stub.run("creative_reasoning", {"note": "context assembly is separate and selective"})
    model_run = ModelRun(
        provider_id=provider.id if provider else None,
        capability="creative_reasoning",
        status=result.status,
        started_at=utcnow(),
        finished_at=utcnow(),
        input_refs=result.output,
        output_refs={},
        cost=None,
        latency_ms=None,
        error=result.error,
    )
    session.add(model_run)
    session.flush()
    return {"id": model_run.id, "status": result.status, "error": result.error}


def _creative_or_404(session: Session, creative_id: str) -> Creative:
    creative = session.get(Creative, creative_id)
    if creative is None:
        raise HTTPException(status_code=404, detail="creative not found")
    return creative


def _current_version(session: Session, creative: Creative) -> StoryLockVersion:
    if not creative.current_approved_story_lock_version_id:
        raise HTTPException(status_code=404, detail="no current story lock")
    version = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="story lock version missing")
    return version
