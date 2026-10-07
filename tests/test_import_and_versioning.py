import pytest
from sqlalchemy import func, select

from creative_os.config import repo_root
from creative_os.importers.handoff import import_handoff
from creative_os.models import (
    ApprovalEvent,
    Asset,
    Creative,
    RegressionTest,
    SkillArtifact,
    SkillVersion,
    SourceArtifact,
    StaleArtifactRecord,
    StoryLockVersion,
)
from creative_os.models.entities import ImmutableVersionError
from creative_os.services.diff import document_diff
from creative_os.services.story_locks import apply_story_lock_correction

pytestmark = pytest.mark.core


def test_import_is_idempotent_and_counts_contracts(session) -> None:
    root = repo_root() / "source_snapshots/2026-10-05"
    first = import_handoff(session, root)
    session.flush()
    skills = session.scalar(select(func.count()).select_from(SkillArtifact))
    skill_files = session.scalar(
        select(func.count()).select_from(SkillVersion).where(SkillVersion.version_label == "handoff-2026-10-05")
    )
    regressions = session.scalar(select(func.count()).select_from(RegressionTest))
    sources = session.scalar(select(func.count()).select_from(SourceArtifact))
    assert skills == 15
    assert skill_files == 15
    assert regressions == 19
    assert sources == 111
    assert first.inserted > 0
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    assert creative is not None
    assert creative.current_approved_story_lock_version_id is not None
    version = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    assert version is not None
    assert version.content_json["floating_hook"] == "my birthday is literally today 😭"
    assert version.content_json["economics"]["total"] == "19.23"
    qa = session.scalar(select(SkillArtifact).where(SkillArtifact.slug == "production-spec-qa"))
    qa_version = session.scalar(select(SkillVersion).where(SkillVersion.skill_id == qa.id))
    assert "my birthday is literally tomorrow" in qa_version.content
    second = import_handoff(session, root)
    session.flush()
    assert second.inserted == 0
    assert session.scalar(select(func.count()).select_from(StoryLockVersion)) == 1


def test_human_correction_versions_lock_and_marks_assets_stale(session) -> None:
    import_handoff(session, repo_root() / "source_snapshots/2026-10-05")
    session.flush()
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    assert creative is not None
    original_id = creative.current_approved_story_lock_version_id
    original = session.get(StoryLockVersion, original_id)
    assert original is not None
    original_hash = original.content_hash
    original_hook = original.content_json["floating_hook"]
    bound = session.scalars(select(Asset).where(Asset.bound_story_lock_version_id == original.id)).all()
    assert bound, "expected current finals to be bound to the imported lock"
    updated = apply_story_lock_correction(
        session,
        creative,
        {"floating_hook": "my birthday is literally tonight 😭"},
        actor="Tyrel",
        reason="Example human correction for versioning. Not a creative-policy change.",
    )
    session.flush()
    session.refresh(original)
    assert original.content_hash == original_hash
    assert original.content_json["floating_hook"] == original_hook
    assert updated.version_number == 2
    assert updated.supersedes_version_id == original.id
    changed = document_diff(original.content_json, updated.content_json)
    assert changed["floating_hook"]["to"].endswith("tonight 😭")
    assert creative.current_approved_story_lock_version_id == updated.id
    approval = session.scalar(
        select(ApprovalEvent).where(ApprovalEvent.version_id == updated.id, ApprovalEvent.status == "APPROVED")
    )
    assert approval is not None
    assert approval.actor == "Tyrel"
    stale = session.scalars(select(StaleArtifactRecord)).all()
    assert stale
    by_name = {asset.name: asset for asset in bound}
    assert by_name["Target S1 final"].staleness_state == "STALE"
    assert by_name["Target S2 final"].stale is False
    assert by_name["Target S3 final"].stale is False
    assert by_name["Tyrel's AirPods 5 Target screenshot"].stale is False
    assert by_name["S2 product images"].stale is False
    assert by_name["AirPods 5 box photo"].stale is False
    assert updated.document_hash != original.document_hash
    try:
        original.content_markdown = "mutated"
        session.flush()
    except ImmutableVersionError:
        session.rollback()
    else:
        raise AssertionError("approved story lock content was mutated")
