from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import Asset, AssetLockDependency, Creative

# Explicit paths from the handoff. Reusable bases and ingredients are intentionally absent.
KNOWN_DEPENDENCIES: dict[str, list[tuple[str, int | None]]] = {
    "Target S1 final": [
        ("/floating_hook", 0),
        ("/hook", 0),
        ("/dialogue", 0),
        ("/slides/0", 0),
    ],
    "Target S2 final": [
        ("/line_items", 1),
        ("/economics", 1),
        ("/slides/1", 1),
    ],
    "Target S3 final": [
        ("/line_items", 2),
        ("/viral_texture", 2),
        ("/slides/2", 2),
        ("/continuity", 2),
    ],
}


def seed_known_lock_dependencies(session: Session, creative: Creative) -> int:
    added = 0
    session.flush()
    assets = session.scalars(select(Asset).where(Asset.creative_id == creative.id)).all()
    for asset in assets:
        specs = KNOWN_DEPENDENCIES.get(asset.name)
        if not specs:
            continue
        for field_path, slide_index in specs:
            existing = session.scalar(
                select(AssetLockDependency).where(
                    AssetLockDependency.asset_id == asset.id,
                    AssetLockDependency.field_path == field_path,
                )
            )
            if existing:
                continue
            session.add(
                AssetLockDependency(
                    asset_id=asset.id,
                    creative_id=creative.id,
                    field_path=field_path,
                    slide_index=slide_index,
                    dependency_kind="FIELD",
                    notes="Explicit handoff dependency. Not inferred from a shared story-lock binding.",
                    explicit=True,
                )
            )
            added += 1
    return added
