from sqlalchemy import func, select
from sqlalchemy.orm import Session

from creative_os.models import (
    ApprovalEvent,
    Asset,
    Creative,
    StaleArtifactRecord,
    StoryLock,
    StoryLockVersion,
)
from creative_os.models.entities import ImmutableVersionError
from creative_os.schemas.story_lock import StoryLockDocument
from creative_os.services.diff import document_diff
from creative_os.services.projections import replace_version_projections
from creative_os.services.story_lock_render import render_story_lock_markdown
from creative_os.util import sha256_text, utcnow

__all__ = ["ImmutableVersionError", "apply_story_lock_correction", "document_diff"]


def apply_story_lock_correction(
    session: Session,
    creative: Creative,
    changes: dict[str, str | bool | None],
    actor: str,
    reason: str,
) -> StoryLockVersion:
    if not creative.current_approved_story_lock_version_id:
        raise ValueError("creative has no approved story lock version")
    current = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    if current is None:
        raise ValueError("current story lock version is missing")
    document = StoryLockDocument.model_validate(current.content_json)
    unknown = [key for key in changes if key not in StoryLockDocument.model_fields]
    if unknown:
        raise ValueError(f"unknown story lock fields: {', '.join(unknown)}")
    updated = document.model_copy(update=changes)
    story_lock = session.scalar(select(StoryLock).where(StoryLock.creative_id == creative.id))
    if story_lock is None:
        raise ValueError("creative has no story lock identity")
    next_number = session.scalar(
        select(func.max(StoryLockVersion.version_number)).where(StoryLockVersion.story_lock_id == story_lock.id)
    )
    markdown = render_story_lock_markdown(updated)
    payload = updated.model_dump(mode="json")
    version = StoryLockVersion(
        story_lock_id=story_lock.id,
        version_number=(next_number or 0) + 1,
        supersedes_version_id=current.id,
        content_json=payload,
        content_markdown=markdown,
        content_hash=sha256_text(markdown),
        change_reason=reason,
        approved_by=actor,
        source_path=None,
        source_hash=None,
        created_at=utcnow(),
    )
    session.add(version)
    session.flush()
    previous_state = creative.current_approved_story_lock_version_id
    creative.current_approved_story_lock_version_id = version.id
    session.add(
        ApprovalEvent(
            object_type="story_lock_version",
            object_id=story_lock.id,
            version_id=version.id,
            status="APPROVED",
            actor=actor,
            notes=reason,
            previous_state=previous_state,
            created_at=utcnow(),
        )
    )
    replace_version_projections(session, version, updated, creative.id)
    _mark_previous_assets_stale(session, creative, current.id, version.id, reason)
    return version


def _mark_previous_assets_stale(
    session: Session,
    creative: Creative,
    previous_version_id: str,
    new_version_id: str,
    reason: str,
) -> None:
    assets = session.scalars(
        select(Asset).where(
            Asset.creative_id == creative.id,
            Asset.bound_story_lock_version_id == previous_version_id,
        )
    ).all()
    for asset in assets:
        asset.stale = True
        session.add(
            StaleArtifactRecord(
                asset_id=asset.id,
                story_lock_version_id=previous_version_id,
                superseded_by_version_id=new_version_id,
                reason=reason,
                created_at=utcnow(),
            )
        )
