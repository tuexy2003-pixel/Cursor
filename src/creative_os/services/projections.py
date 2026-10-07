from sqlalchemy.orm import Session

from creative_os.models import (
    CommentDoor,
    ContinuityEntry,
    SlideProjection,
    StoryLineItem,
    StoryLockVersion,
    ViralTextureDetail,
)
from creative_os.schemas.story_lock import StoryLockDocument


def replace_version_projections(
    session: Session,
    version: StoryLockVersion,
    document: StoryLockDocument,
    creative_id: str,
) -> None:
    session.query(StoryLineItem).filter(StoryLineItem.story_lock_version_id == version.id).delete()
    session.query(SlideProjection).filter(SlideProjection.story_lock_version_id == version.id).delete()
    session.query(ContinuityEntry).filter(ContinuityEntry.story_lock_version_id == version.id).delete()
    session.query(ViralTextureDetail).filter(ViralTextureDetail.story_lock_version_id == version.id).delete()
    session.query(CommentDoor).filter(CommentDoor.story_lock_version_id == version.id).delete()

    for item in document.line_items:
        session.add(
            StoryLineItem(
                story_lock_version_id=version.id,
                position=item.position,
                title=item.title,
                quantity=item.quantity,
                unit_price=item.unit_price,
                model=item.model,
                generation=item.generation,
                variant=item.variant,
                color=item.color,
                pack_count=item.pack_count,
                external_id=item.external_id,
            )
        )
    for slide in document.slides:
        session.add(
            SlideProjection(
                story_lock_version_id=version.id,
                slide_index=slide.index,
                beat=slide.beat,
                relative_time=slide.relative_time,
                visible_clock=slide.visible_clock,
                visible_date=slide.visible_date,
                overlay=slide.overlay,
                order_state=slide.order_state,
                actor_knowledge=slide.actor_knowledge,
                actor_location=slide.actor_location,
            )
        )
    for fact in document.continuity:
        session.add(
            ContinuityEntry(
                story_lock_version_id=version.id,
                slide_index=fact.slide_index,
                field=fact.field,
                value=fact.value,
            )
        )
    for detail in document.viral_texture:
        session.add(
            ViralTextureDetail(
                story_lock_version_id=version.id,
                slide_index=detail.slide_index,
                text=detail.text,
                category=detail.category,
            )
        )
    for door in document.comment_doors:
        session.add(
            CommentDoor(
                creative_id=creative_id,
                story_lock_version_id=version.id,
                kind=door.kind,
                text=door.text,
                prediction_notes="Imported from the story lock. Actual comments are not in the core handoff.",
            )
        )
