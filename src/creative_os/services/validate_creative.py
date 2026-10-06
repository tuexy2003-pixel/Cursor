from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import (
    ApprovalEvent,
    Asset,
    AssetRelation,
    Creative,
    StaleArtifactRecord,
    StoryLockVersion,
)
from creative_os.schemas.story_lock import StoryLockDocument
from creative_os.services.product_identity import product_identifier_findings
from creative_os.validation.checks import (
    approval_status,
    arithmetic_status,
    aspect_ratio_status,
    line_items_subtotal_status,
    lock_precedence_status,
    product_match_status,
    provenance_status,
    recursive_edit_status,
    rights_export_status,
    timeline_order_status,
    weekday_status,
)


def validate_creative(session: Session, creative: Creative) -> list[tuple[str, str, str]]:
    results: list[tuple[str, str, str]] = []
    version_id = creative.current_approved_story_lock_version_id
    if version_id is None:
        results.append(("current_lock", "NOT_APPLICABLE", "no approved story lock"))
        return results
    version = session.get(StoryLockVersion, version_id)
    if version is None:
        results.append(("version_consistency", "FAIL", "current pointer does not resolve"))
        return results
    if version.story_lock_id != _lock_id(session, creative):
        results.append(("version_consistency", "FAIL", "current version belongs to another lock"))
    else:
        results.append(("version_consistency", "PASS", f"version {version.version_number} is current"))
    document = StoryLockDocument.model_validate(version.content_json)
    if document.economics:
        status, message = arithmetic_status(
            document.economics.subtotal,
            document.economics.discount,
            document.economics.tax,
            document.economics.total,
        )
        results.append(("arithmetic", status, message))
        status, message = line_items_subtotal_status(document.line_items, document.economics.subtotal)
        results.append(("line_item_subtotal", status, message))
    else:
        results.append(("arithmetic", "NOT_APPLICABLE", "no economics on the lock"))
    findings = product_identifier_findings(document, version.content_markdown or "")
    if not findings:
        results.append(
            (
                "product_identifier",
                "PASS",
                "no line item keeps an identifier the lock text assigns to a superseded model",
            )
        )
    for row in findings:
        results.append(
            (
                f"product_identifier:{row['identifier']}",
                row["status"],
                (
                    f"{row['identifier_kind']} {row['identifier']} is known to belong to "
                    f"{row['known_owner']}, not {row['title']}"
                ),
            )
        )
    if document.story_date and document.story_weekday:
        status, message = weekday_status(document.story_date, document.story_weekday)
        results.append(("story_weekday", status, message))
    clocks = [slide.visible_clock for slide in document.slides]
    status, message = timeline_order_status(clocks)
    results.append(("timeline_order", status, message))
    pickup = _pickup_weekday(document)
    if document.story_date and pickup:
        from datetime import date, timedelta

        story = date.fromisoformat(document.story_date)
        # The pickup token is a weekday name. Search the next 14 days for that weekday
        # only when the visible date also contains a day number we already trust via
        # an explicit ISO in continuity. Here we validate the claimed weekday of a
        # date string embedded as "Oct 7" only when story year is known and the token
        # includes a parseable month/day handled by the caller. This check uses the
        # lock's own continuity value when it embeds a known ISO-compatible phrase.
        target = _explicit_pickup_date(document, story.year)
        if target is not None:
            status, message = weekday_status(target.isoformat(), pickup)
            results.append(("pickup_weekday", status, message))
            if target < story:
                results.append(("pickup_order", "FAIL", "pickup date is before the story date"))
            elif target - story > timedelta(days=14):
                results.append(("pickup_order", "WARNING", "pickup is more than 14 days after the story date"))
            else:
                results.append(("pickup_order", "PASS", "pickup date follows the story date"))
    approved = session.scalar(
        select(ApprovalEvent.id).where(
            ApprovalEvent.version_id == version.id,
            ApprovalEvent.status == "APPROVED",
        )
    )
    status, message = approval_status(approved is not None, required=True)
    results.append(("required_approval", status, message))
    lock_models = [item.model for item in document.line_items if item.model]
    assets = list(session.scalars(select(Asset).where(Asset.creative_id == creative.id)).all())
    if assets:
        owned_ids = [asset.id for asset in assets]
        related_ids = session.scalars(
            select(AssetRelation.related_asset_id).where(AssetRelation.asset_id.in_(owned_ids))
        ).all()
        known = {asset.id for asset in assets}
        for related_id in related_ids:
            if related_id in known:
                continue
            related = session.get(Asset, related_id)
            if related is not None:
                assets.append(related)
                known.add(related.id)
    if not assets:
        results.append(("assets", "NOT_APPLICABLE", "no assets linked to this creative"))
    for asset in assets:
        if asset.product_model:
            status, message = lock_precedence_status(asset.product_model, lock_models, asset.stale, False)
        else:
            status, message = product_match_status(lock_models, None)
        results.append((f"product:{asset.name}", status, message))
        status, message = provenance_status(
            asset.role,
            asset.rights_status,
            asset.original_path,
            asset.content_hash,
            file_expected=asset.present_in_snapshot,
        )
        results.append((f"provenance:{asset.name}", status, message))
        if asset.role == "BASE":
            status, message = rights_export_status(asset.role, asset.rights_status, True)
            results.append((f"rights_export:{asset.name}", status, message))
        if asset.role != "EXAMPLE":
            results.append(
                (
                    f"aspect:{asset.name}",
                    "NOT_APPLICABLE",
                    "the 9:19.6 ratio is a program preference for deliverable examples",
                )
            )
        elif asset.width and asset.height:
            status, message = aspect_ratio_status(asset.width, asset.height)
            results.append((f"aspect:{asset.name}", status, message))
        else:
            results.append((f"aspect:{asset.name}", "WARNING", "deliverable example has no dimensions"))
        status, message = _lineage_status(session, asset)
        results.append((f"lineage:{asset.name}", status, message))
        if asset.bound_story_lock_version_id and asset.bound_story_lock_version_id != version.id:
            stale = session.scalar(
                select(StaleArtifactRecord.id).where(StaleArtifactRecord.asset_id == asset.id)
            )
            if asset.stale or stale is not None:
                results.append((f"stale:{asset.name}", "PASS", "older asset is marked stale"))
            else:
                results.append(
                    (
                        f"stale:{asset.name}",
                        "FAIL",
                        "asset is bound to a superseded lock and is not marked stale",
                    )
                )
    return results


def _lineage_status(session: Session, asset: Asset) -> tuple[str, str]:
    if asset.role != "EXAMPLE":
        return "NOT_APPLICABLE", "lineage check applies to edited deliverables"
    relations = session.scalars(
        select(AssetRelation).where(AssetRelation.asset_id == asset.id, AssetRelation.relation == "BASE")
    ).all()
    if not relations:
        return recursive_edit_status(None)
    parents = [session.get(Asset, relation.related_asset_id) for relation in relations]
    if any(parent is None for parent in parents):
        return "FAIL", "a base relation points at a missing asset"
    if all(parent is not None and parent.role == "BASE" for parent in parents):
        return recursive_edit_status(True)
    return recursive_edit_status(False)


def _lock_id(session: Session, creative: Creative) -> str | None:
    from creative_os.models import StoryLock

    lock = session.scalar(select(StoryLock).where(StoryLock.creative_id == creative.id))
    return lock.id if lock else None


def _pickup_weekday(document: StoryLockDocument) -> str | None:
    for slide in document.slides:
        if slide.visible_date and "Wed" in slide.visible_date:
            return "Wednesday"
        if slide.visible_date:
            for name in (
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ):
                if name[:3] in slide.visible_date or name in slide.visible_date:
                    return name
    return None


def _explicit_pickup_date(document: StoryLockDocument, year: int):
    import re
    from datetime import date

    months = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }
    for slide in document.slides:
        if not slide.visible_date:
            continue
        match = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2})", slide.visible_date)
        if match and match.group(1) in months:
            return date(year, months[match.group(1)], int(match.group(2)))
    return None
