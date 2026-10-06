from sqlalchemy.orm import Session

from creative_os.models import (
    Account,
    Asset,
    Campaign,
    Comment,
    CommentCluster,
    CommentDoor,
    Creative,
    CreativeGenome,
    Experiment,
    ExperimentVariant,
    Post,
    StoryLockVersion,
)


class ConsistencyError(ValueError):
    pass


_REUSABLE_ROLES = {"BASE", "INGREDIENT", "REFERENCE", "EVIDENCE"}
_STALE_STATES = {"STALE", "STALE_REVIEW_REQUIRED"}


def resolve_post_attribution(
    session: Session,
    *,
    creative: Creative | None,
    account_id: str | None,
    campaign_id: str | None,
    story_lock_version_id: str | None,
    creative_genome_id: str | None,
    assets: list[Asset],
    attribution_mode: str,
) -> tuple[str | None, str | None, str | None]:
    if attribution_mode not in {"CURRENT_PUBLISH", "HISTORICAL_BACKFILL"}:
        raise ConsistencyError("attribution_mode must be CURRENT_PUBLISH or HISTORICAL_BACKFILL")
    resolved_account = account_id
    if creative and creative.account_id:
        if resolved_account is None:
            resolved_account = creative.account_id
        elif resolved_account != creative.account_id:
            raise ConsistencyError("post account does not match the creative account")
    resolved_campaign = campaign_id
    if creative and creative.campaign_id:
        if resolved_campaign is None:
            resolved_campaign = creative.campaign_id
        elif resolved_campaign != creative.campaign_id:
            raise ConsistencyError("post campaign does not match the creative campaign")
    genome_id = _resolve_genome(session, creative, story_lock_version_id, creative_genome_id)
    if attribution_mode == "CURRENT_PUBLISH":
        for asset in assets:
            if (
                asset.bound_story_lock_version_id
                and story_lock_version_id
                and asset.bound_story_lock_version_id != story_lock_version_id
            ):
                raise ConsistencyError(f"asset {asset.name} is bound to a different story lock")
            if asset.role not in _REUSABLE_ROLES and (asset.stale or asset.staleness_state in _STALE_STATES):
                raise ConsistencyError(f"stale deliverable {asset.name} cannot be published as current")
    return resolved_account, resolved_campaign, genome_id


def _resolve_genome(
    session: Session,
    creative: Creative | None,
    story_lock_version_id: str | None,
    creative_genome_id: str | None,
) -> str | None:
    if creative_genome_id:
        genome = session.get(CreativeGenome, creative_genome_id)
        if genome is None:
            raise ConsistencyError("creative genome was not found")
        if creative is None or genome.creative_id != creative.id:
            raise ConsistencyError("creative genome belongs to a different creative")
        if genome.source_story_lock_version_id != story_lock_version_id:
            raise ConsistencyError("creative genome describes a different story lock version")
        return genome.id
    if creative is None or not creative.current_genome_id or not story_lock_version_id:
        return None
    genome = session.get(CreativeGenome, creative.current_genome_id)
    if genome is None:
        return None
    if genome.creative_id != creative.id or genome.source_story_lock_version_id != story_lock_version_id:
        return None
    if genome.approval_state != "APPROVED":
        return None
    return genome.id


def validate_post(
    session: Session,
    *,
    creative: Creative | None,
    account: Account | None,
    campaign: Campaign | None,
    story_lock: StoryLockVersion | None,
    variant: ExperimentVariant | None,
    assets: list[Asset],
) -> None:
    if creative and account and creative.account_id and creative.account_id != account.id:
        raise ConsistencyError("post account does not match the creative account")
    if creative and account and creative.program_id != account.program_id:
        raise ConsistencyError("post account and creative belong to different programs")
    if campaign and creative and campaign.program_id != creative.program_id:
        raise ConsistencyError("campaign and creative belong to different programs")
    if campaign and account and campaign.account_id and campaign.account_id != account.id:
        raise ConsistencyError("campaign account does not match the post account")
    if story_lock is not None:
        if creative is None:
            raise ConsistencyError("a story lock version requires a creative")
        from creative_os.models import StoryLock

        lock = session.get(StoryLock, story_lock.story_lock_id)
        if lock is None or lock.creative_id != creative.id:
            raise ConsistencyError("story lock version does not belong to the creative")
    if variant is not None:
        experiment = session.get(Experiment, variant.experiment_id)
        if experiment is None:
            raise ConsistencyError("experiment variant has no experiment")
        if creative and experiment.creative_id and experiment.creative_id != creative.id:
            raise ConsistencyError("experiment variant belongs to a different creative")
        if account and experiment.account_id and experiment.account_id != account.id:
            raise ConsistencyError("experiment variant belongs to a different account")
    for asset in assets:
        if creative and asset.creative_id and asset.creative_id != creative.id:
            raise ConsistencyError(f"asset {asset.name} belongs to a different creative")


def validate_door_mapping(
    session: Session,
    door: CommentDoor | None,
    cluster: CommentCluster,
) -> None:
    if door is None:
        return
    post = session.get(Post, cluster.post_id)
    if post is None:
        raise ConsistencyError("cluster post is missing")
    if not post.creative_id or not post.story_lock_version_id:
        raise ConsistencyError(
            "post is missing the creative or story lock identity required to map a predicted door"
        )
    if post.creative_id and door.creative_id != post.creative_id:
        raise ConsistencyError("comment door belongs to a different creative than the post")
    if (
        door.story_lock_version_id
        and post.story_lock_version_id
        and door.story_lock_version_id != post.story_lock_version_id
    ):
        raise ConsistencyError("comment door is bound to a different story lock than the published post")


def validate_cluster_comments(session: Session, cluster_post_id: str, comment_ids: list[str]) -> list[Comment]:
    comments: list[Comment] = []
    for comment_id in comment_ids:
        comment = session.get(Comment, comment_id)
        if comment is None:
            raise ConsistencyError(f"comment {comment_id} was not found")
        if comment.post_id != cluster_post_id:
            raise ConsistencyError("cluster cannot contain a comment from another post")
        comments.append(comment)
    return comments
