from typing import Any

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from creative_os.models import (
    ApprovalEvent,
    Asset,
    AssetLockDependency,
    Creative,
    StaleArtifactRecord,
    StoryLock,
    StoryLockVersion,
)
from creative_os.models.entities import ImmutableVersionError
from creative_os.schemas.story_lock import FieldPatch, StoryLockDocument
from creative_os.services.canonical import document_hash
from creative_os.services.diff import changed_paths, document_diff
from creative_os.services.projections import replace_version_projections
from creative_os.services.story_lock_render import render_canonical_markdown
from creative_os.util import sha256_text, utcnow

__all__ = [
    "ImmutableVersionError",
    "apply_story_lock_correction",
    "decide_story_lock_version",
    "document_diff",
    "propose_story_lock_change",
]

_REUSABLE_ROLES = {"BASE", "INGREDIENT", "REFERENCE", "EVIDENCE"}


def apply_story_lock_correction(
    session: Session,
    creative: Creative,
    changes: dict[str, Any],
    actor: str,
    reason: str,
    patches: list[FieldPatch] | None = None,
) -> StoryLockVersion:
    """Trusted human path. The API must pass the server operator, not request JSON."""
    return _write_version(
        session,
        creative,
        changes,
        patches or [],
        actor=actor,
        reason=reason,
        approval_state="APPROVED",
        move_pointer=True,
    )


def propose_story_lock_change(
    session: Session,
    creative: Creative,
    changes: dict[str, Any],
    proposer: str,
    reason: str,
    patches: list[FieldPatch] | None = None,
) -> StoryLockVersion:
    """A proposal never moves the current-approved pointer, even if the proposer name matches the operator."""
    return _write_version(
        session,
        creative,
        changes,
        patches or [],
        actor=proposer,
        reason=reason,
        approval_state="PENDING",
        move_pointer=False,
    )


def decide_story_lock_version(
    session: Session,
    creative: Creative,
    version: StoryLockVersion,
    decision: str,
    actor: str,
    notes: str | None,
) -> StoryLockVersion:
    allowed = {"APPROVE", "REJECT", "NEEDS_CHANGES"}
    if decision not in allowed:
        raise ValueError(f"decision must be one of {', '.join(sorted(allowed))}")
    if version.approval_state != "PENDING" and decision != "APPROVE":
        raise ValueError("only a pending proposal can be rejected or sent back")
    previous_state = creative.current_approved_story_lock_version_id
    if decision == "APPROVE" and version.approval_state == "PENDING":
        creative.current_approved_story_lock_version_id = version.id
    session.add(
        ApprovalEvent(
            object_type="story_lock_version",
            object_id=version.story_lock_id,
            version_id=version.id,
            status=decision if decision != "APPROVE" else "APPROVED",
            actor=actor,
            notes=notes,
            previous_state=previous_state,
            created_at=utcnow(),
        )
    )
    return version


def build_document(
    current: StoryLockDocument,
    changes: dict[str, Any],
    patches: list[FieldPatch],
) -> StoryLockDocument:
    unknown = [key for key in changes if key not in StoryLockDocument.model_fields]
    if unknown:
        raise ValueError(f"unknown story lock fields: {', '.join(unknown)}")
    payload = current.model_dump(mode="json")
    payload.update(changes)
    for patch in patches:
        _set_path(payload, patch.path, patch.value)
    try:
        return StoryLockDocument.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"story lock validation failed: {exc}") from exc


def _write_version(
    session: Session,
    creative: Creative,
    changes: dict[str, Any],
    patches: list[FieldPatch],
    *,
    actor: str,
    reason: str,
    approval_state: str,
    move_pointer: bool,
) -> StoryLockVersion:
    if not creative.current_approved_story_lock_version_id:
        raise ValueError("creative has no approved story lock version")
    current = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    if current is None:
        raise ValueError("current story lock version is missing")
    document = StoryLockDocument.model_validate(current.content_json)
    updated = build_document(document, changes, patches)
    story_lock = session.scalar(select(StoryLock).where(StoryLock.creative_id == creative.id))
    if story_lock is None:
        raise ValueError("creative has no story lock identity")
    next_number = session.scalar(
        select(func.max(StoryLockVersion.version_number)).where(StoryLockVersion.story_lock_id == story_lock.id)
    )
    markdown = render_canonical_markdown(updated)
    payload = updated.model_dump(mode="json")
    version = StoryLockVersion(
        story_lock_id=story_lock.id,
        version_number=(next_number or 0) + 1,
        supersedes_version_id=current.id,
        content_json=payload,
        content_markdown=markdown,
        content_hash=sha256_text(markdown),
        document_hash=document_hash(updated),
        approval_state=approval_state,
        change_reason=reason,
        approved_by=actor if approval_state == "APPROVED" else None,
        source_path=None,
        source_hash=None,
        created_at=utcnow(),
    )
    session.add(version)
    session.flush()
    previous_state = creative.current_approved_story_lock_version_id
    if move_pointer:
        creative.current_approved_story_lock_version_id = version.id
    session.add(
        ApprovalEvent(
            object_type="story_lock_version",
            object_id=story_lock.id,
            version_id=version.id,
            status=approval_state,
            actor=actor,
            notes=reason,
            previous_state=previous_state,
            created_at=utcnow(),
        )
    )
    replace_version_projections(session, version, updated, creative.id)
    if move_pointer:
        paths = changed_paths(current.content_json, payload)
        _mark_affected_assets_stale(session, creative, current.id, version.id, paths, reason)
    return version


def _set_path(payload: dict[str, Any], path: str, value: object) -> None:
    if not path.startswith("/"):
        raise ValueError(f"patch path must start with /: {path}")
    parts = [part for part in path.split("/") if part]
    if not parts:
        raise ValueError("empty patch path")
    cursor: Any = payload
    for part in parts[:-1]:
        cursor = _step(cursor, part, path)
        if cursor is None:
            raise ValueError(f"patch path missing parent: {path}")
    _assign(cursor, parts[-1], value, path)


def _step(cursor: Any, part: str, path: str) -> Any:
    if isinstance(cursor, list):
        index = _index(part, path)
        if index >= len(cursor):
            raise ValueError(f"patch path out of range: {path}")
        return cursor[index]
    if isinstance(cursor, dict):
        if part not in cursor:
            raise ValueError(f"patch path missing parent: {path}")
        return cursor[part]
    raise ValueError(f"patch path cannot enter {path}")


def _assign(cursor: Any, part: str, value: object, path: str) -> None:
    if isinstance(cursor, list):
        index = _index(part, path)
        if index >= len(cursor):
            raise ValueError(f"patch path out of range: {path}")
        cursor[index] = value
        return
    if isinstance(cursor, dict):
        cursor[part] = value
        return
    raise ValueError(f"patch path cannot enter {path}")


def _index(part: str, path: str) -> int:
    if not part.isdigit():
        raise ValueError(f"patch path expected a list index in {path}")
    return int(part)


def paths_intersect(changed: str, dependency: str) -> bool:
    return changed == dependency or changed.startswith(dependency + "/") or dependency.startswith(changed + "/")


def _mark_affected_assets_stale(
    session: Session,
    creative: Creative,
    previous_version_id: str,
    new_version_id: str,
    paths: list[str],
    reason: str,
) -> None:
    assets = session.scalars(
        select(Asset).where(
            Asset.creative_id == creative.id,
            Asset.bound_story_lock_version_id == previous_version_id,
        )
    ).all()
    dependencies = session.scalars(
        select(AssetLockDependency).where(AssetLockDependency.creative_id == creative.id)
    ).all()
    by_asset: dict[str, list[AssetLockDependency]] = {}
    for row in dependencies:
        by_asset.setdefault(row.asset_id, []).append(row)
    for asset in assets:
        deps = by_asset.get(asset.id, [])
        matched = [
            dep.field_path for dep in deps if any(paths_intersect(path, dep.field_path) for path in paths)
        ]
        if matched:
            _record_stale(session, asset, previous_version_id, new_version_id, "STALE", reason)
            continue
        if deps:
            continue
        if asset.role in _REUSABLE_ROLES:
            continue
        if asset.role == "EXAMPLE":
            _record_stale(
                session,
                asset,
                previous_version_id,
                new_version_id,
                "STALE_REVIEW_REQUIRED",
                f"{reason} Dependency relationship is unknown.",
            )


def _record_stale(
    session: Session,
    asset: Asset,
    previous_version_id: str,
    new_version_id: str,
    state: str,
    reason: str,
) -> None:
    asset.stale = True
    asset.staleness_state = state
    session.add(
        StaleArtifactRecord(
            asset_id=asset.id,
            story_lock_version_id=previous_version_id,
            superseded_by_version_id=new_version_id,
            staleness_state=state,
            reason=reason,
            created_at=utcnow(),
        )
    )
