from sqlalchemy import func, select
from sqlalchemy.orm import Session

from creative_os.models import (
    BenchmarkCreative,
    Creative,
    MechanicObservation,
    PolicyRule,
    SkillArtifact,
    SkillVersion,
    StoryLockVersion,
)


def assemble_context(session: Session, creative: Creative, limit: int = 8) -> dict[str, object]:
    """Select the context a future creative provider would receive. Does not dump the database."""
    global_rules = session.scalars(
        select(PolicyRule).where(PolicyRule.scope_level == "GLOBAL", PolicyRule.status == "active").limit(limit)
    ).all()
    program_rules = session.scalars(
        select(PolicyRule)
        .where(
            PolicyRule.scope_level == "PROGRAM",
            PolicyRule.scope_id == creative.program_id,
            PolicyRule.status == "active",
        )
        .limit(limit)
    ).all()
    current_ids = [
        row.current_version_id for row in session.scalars(select(SkillArtifact)).all() if row.current_version_id
    ]
    if current_ids:
        skills = session.scalars(
            select(SkillVersion).where(SkillVersion.id.in_(current_ids), SkillVersion.status.like("ACTIVE%"))
        ).all()
    else:
        skills = session.scalars(
            select(SkillVersion).where(SkillVersion.status.like("ACTIVE%")).limit(limit)
        ).all()
    lock = None
    if creative.current_approved_story_lock_version_id:
        lock = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    benchmarks = session.scalars(
        select(BenchmarkCreative).where(BenchmarkCreative.holdout.is_(False)).limit(limit)
    ).all()
    mechanics = session.execute(
        select(MechanicObservation.dimension, MechanicObservation.value, func.count())
        .group_by(MechanicObservation.dimension, MechanicObservation.value)
        .limit(limit)
    ).all()
    return {
        "creative_id": creative.id,
        "global_policy_codes": [rule.code for rule in global_rules],
        "program_policy_codes": [rule.code for rule in program_rules],
        "active_skill_ids": [skill.id for skill in skills],
        "story_lock_version_id": lock.id if lock else None,
        "benchmark_names": [row.name for row in benchmarks],
        "holdouts_excluded": True,
        "mechanic_counts": [{"dimension": row[0], "value": row[1], "count": row[2]} for row in mechanics],
    }
