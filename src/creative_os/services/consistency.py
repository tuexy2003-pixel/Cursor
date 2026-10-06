from sqlalchemy.orm import Session

from creative_os.models import (
    Account,
    Asset,
    Campaign,
    Comment,
    CommentCluster,
    CommentDoor,
    Creative,
    Experiment,
    ExperimentVariant,
    Post,
    StoryLockVersion,
)


class ConsistencyError(ValueError):
    pass


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
