from typing import Any

from fastapi import APIRouter, Depends, HTTPException
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
    CommentDoor,
    CommentDoorMapping,
    Creative,
    Experiment,
    ExperimentVariant,
    GenomeFacet,
    MechanicObservation,
    ModelProvider,
    ModelRun,
    PerformanceSnapshot,
    PolicyRule,
    Post,
    Program,
    ReferenceBank,
    RegressionTest,
    SkillArtifact,
    SkillVersion,
    SourceArtifact,
    StaleArtifactRecord,
    StoryLineItem,
    StoryLock,
    StoryLockVersion,
    ValidationResult,
    ValidationRun,
)
from creative_os.providers.stub import StubProvider
from creative_os.schemas.story_lock import StoryLockCorrection, StoryLockDocument
from creative_os.services.context import assemble_context
from creative_os.services.diff import document_diff
from creative_os.services.story_lock_render import render_story_lock_markdown
from creative_os.services.story_locks import apply_story_lock_correction
from creative_os.services.validate_creative import validate_creative
from creative_os.util import utcnow
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


class PostIn(BaseModel):
    platform: str = "tiktok"
    creative_id: str | None = None
    account_id: str | None = None
    url: str | None = None
    notes: str | None = None


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
        profile = session.scalar(
            select(AccountDnaProfile)
            .where(AccountDnaProfile.account_id == row.id)
            .order_by(AccountDnaProfile.version_number.desc())
        )
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
        document_diff(previous.content_json, current.content_json)
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
        "context_preview": assemble_context(session, creative),
    }


def _lock_version(session: Session, creative_id: str, token: str) -> StoryLockVersion | None:
    found = session.get(StoryLockVersion, token)
    if found is not None:
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
    from creative_os.models import CreativeGenome

    genome = session.scalar(
        select(CreativeGenome)
        .where(CreativeGenome.creative_id == creative_id)
        .order_by(CreativeGenome.created_at.desc())
    )
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
    return {"markdown": render_story_lock_markdown(document), "version_id": version.id}


@router.get("/creatives/{creative_id}/story-lock/diff")
def lock_diff(
    creative_id: str,
    left: str,
    right: str,
    session: Session = Depends(session_dep),
) -> dict[str, object]:
    _creative_or_404(session, creative_id)
    older = _lock_version(session, creative_id, left)
    newer = _lock_version(session, creative_id, right)
    if older is None or newer is None:
        raise HTTPException(status_code=404, detail="story lock version not found")
    return {"changes": document_diff(older.content_json, newer.content_json)}


@router.post("/creatives/{creative_id}/story-lock/corrections")
def correct_lock(
    creative_id: str,
    body: StoryLockCorrection,
    session: Session = Depends(session_dep),
) -> dict[str, object]:
    creative = _creative_or_404(session, creative_id)
    try:
        version = apply_story_lock_correction(session, creative, body.changes, body.actor, body.reason)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "version_id": version.id,
        "version_number": version.version_number,
        "supersedes_version_id": version.supersedes_version_id,
        "content_hash": version.content_hash,
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
    if body.control_changes.keys() & body.variant_changes.keys() and set(body.control_changes) == set(
        body.variant_changes
    ):
        if body.control_changes == body.variant_changes:
            raise HTTPException(
                status_code=400,
                detail="control and variant change the same values; isolate one dimension",
            )
    experiment = Experiment(
        name=body.name,
        hypothesis=body.hypothesis,
        account_id=body.account_id,
        campaign_id=body.campaign_id,
        creative_id=body.creative_id,
        variable_dimension=body.variable_dimension,
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
    post = Post(
        creative_id=body.creative_id,
        account_id=body.account_id,
        platform=body.platform,
        url=body.url,
        notes=body.notes,
        published_at=None,
        created_at=utcnow(),
    )
    session.add(post)
    session.flush()
    return {"id": post.id}


@router.post("/posts/{post_id}/snapshots")
def add_snapshot(post_id: str, body: SnapshotIn, session: Session = Depends(session_dep)) -> dict[str, str]:
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    snap = PerformanceSnapshot(
        post_id=post.id,
        source=body.source,
        captured_at=utcnow(),
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
    cluster = CommentCluster(
        post_id=post_id,
        label=body.label,
        size=body.size,
        example_comments=body.example_comments,
        sentiment=None,
        confidence=None,
        unexpected=body.unexpected,
        created_at=utcnow(),
    )
    session.add(cluster)
    session.flush()
    relationship = body.relationship
    if body.door_id is None and body.unexpected:
        relationship = "unexpected"
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
def novelty(session: Session = Depends(session_dep)) -> list[dict[str, object]]:
    rows = session.execute(
        select(
            MechanicObservation.dimension,
            MechanicObservation.value,
            func.count(),
            func.max(MechanicObservation.observed_at),
        ).group_by(MechanicObservation.dimension, MechanicObservation.value)
    ).all()
    return [
        {
            "dimension": row[0],
            "value": row[1],
            "count": row[2],
            "latest": row[3].isoformat() if row[3] is not None else None,
        }
        for row in rows
    ]


@router.get("/runs")
def runs(session: Session = Depends(session_dep)) -> dict[str, object]:
    providers = session.scalars(select(ModelProvider)).all()
    model_runs = session.scalars(select(ModelRun).order_by(ModelRun.started_at.desc())).all()
    validation_runs = session.scalars(select(ValidationRun).order_by(ValidationRun.created_at.desc())).all()
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
        "model_runs": [
            {"id": row.id, "capability": row.capability, "status": row.status, "error": row.error}
            for row in model_runs
        ],
        "validation_runs": [
            {"id": row.id, "subject_type": row.subject_type, "subject_id": row.subject_id}
            for row in validation_runs
        ],
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
