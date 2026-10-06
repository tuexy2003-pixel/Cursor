from datetime import timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from creative_os.models import MechanicObservation, Post
from creative_os.util import utcnow

WINDOWS = ("last_7_days", "last_30_days", "lifetime")


def mechanic_report(session: Session, account_id: str | None) -> dict[str, Any]:
    return {
        "account_id": account_id,
        "source": "mechanic_observations",
        "scope": "ACCOUNT" if account_id else "UNSCOPED",
        "reason_included": "account-local mechanic history; no fatigue score",
        "authority": "observation",
        "version": "windows",
        "windows": {
            "last_7_days": _counts(session, account_id, days=7),
            "last_30_days": _counts(session, account_id, days=30),
            "lifetime": _counts(session, account_id, days=None),
            "last_n_posts": _last_n_posts(session, account_id, 10),
        },
        "program_lifetime": _counts(session, None, days=None),
    }


def _counts(session: Session, account_id: str | None, days: int | None) -> list[dict[str, Any]]:
    query = select(
        MechanicObservation.dimension,
        MechanicObservation.value,
        func.count(),
    ).group_by(MechanicObservation.dimension, MechanicObservation.value)
    if account_id is not None:
        query = query.where(MechanicObservation.account_id == account_id)
    if days is not None:
        query = query.where(MechanicObservation.observed_at >= utcnow() - timedelta(days=days))
    rows = session.execute(query.order_by(MechanicObservation.dimension, MechanicObservation.value)).all()
    return [{"dimension": row[0], "value": row[1], "count": row[2]} for row in rows]


def _last_n_posts(session: Session, account_id: str | None, limit: int) -> list[dict[str, Any]]:
    if account_id is None:
        return []
    posts = session.scalars(
        select(Post)
        .where(Post.account_id == account_id, Post.published_at.is_not(None))
        .order_by(Post.published_at.desc())
        .limit(limit)
    ).all()
    if not posts:
        return []
    post_ids = [post.id for post in posts]
    rows = session.execute(
        select(MechanicObservation.dimension, MechanicObservation.value, func.count())
        .where(MechanicObservation.post_id.in_(post_ids))
        .group_by(MechanicObservation.dimension, MechanicObservation.value)
        .order_by(MechanicObservation.dimension, MechanicObservation.value)
    ).all()
    return [{"dimension": row[0], "value": row[1], "count": row[2], "post_window": limit} for row in rows]
