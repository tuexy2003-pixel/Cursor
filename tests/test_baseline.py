from sqlalchemy import func, select

from creative_os.config import repo_root
from creative_os.importers.examples import UNRESOLVED_RELATIONSHIPS, import_visual_supplements
from creative_os.importers.handoff import import_handoff
from creative_os.models import (
    Asset,
    AssetRelation,
    ExampleLink,
    Experiment,
    ModelRun,
    PolicyRule,
    SkillArtifact,
    SkillVersion,
    StoryLockVersion,
)
from creative_os.services.baseline import EXAMPLE_AFTER, EXAMPLE_BEFORE, apply_preservation_baseline
from creative_os.services.validate_creative import validate_creative


def _seed(session):
    root = repo_root() / "source_snapshots/2026-10-05"
    import_handoff(session, root)
    visual = import_visual_supplements(session, repo_root() / "source_snapshots/supplements/2026-10-05")
    apply_preservation_baseline(session)
    session.flush()
    return visual


def test_clean_baseline_keeps_story_lock_and_adds_binaries(session) -> None:
    visual = _seed(session)
    assert visual["archive_a_files"] == 13
    assert visual["archive_b_files"] == 5
    assert visual["index_matches"] == 8
    assert visual["child_assets"] == 10
    assert session.scalar(select(func.count()).select_from(Experiment)) == 0
    assert session.scalar(select(func.count()).select_from(ModelRun)) == 0
    version = session.scalar(select(StoryLockVersion))
    assert version is not None
    assert version.content_json["floating_hook"] == "my birthday is literally today 😭"
    assert version.content_json["economics"]["total"] == "19.23"
    assert "AirPods 5" in version.content_markdown
    assert "tonight" not in version.content_markdown
    hashed = session.scalar(select(func.count()).select_from(Asset).where(Asset.content_hash.is_not(None)))
    present = session.scalar(select(func.count()).select_from(Asset).where(Asset.present_in_snapshot.is_(True)))
    assert hashed == 18
    assert present == 18
    keyboard = session.scalar(select(Asset).where(Asset.name.startswith("iOS26 Messages keyboard")))
    order = session.scalar(select(Asset).where(Asset.name == "Target order details base"))
    user_base = session.scalar(select(Asset).where(Asset.name == "Tyrel's AirPods 5 Target screenshot"))
    assert keyboard is not None and keyboard.rights_status == "USER_OWNED" and keyboard.stale is False
    assert order is not None and order.rights_status == "UNKNOWN" and order.role == "BASE"
    assert user_base is not None and user_base.stale is False
    airpods4 = session.scalar(select(Asset).where(Asset.name == "3_airpods4.jpg"))
    assert airpods4 is not None and airpods4.stale is True and airpods4.product_model == "AirPods 4"
    assert session.scalar(select(func.count()).select_from(AssetRelation)) >= 18
    assert session.scalar(select(func.count()).select_from(ExampleLink)) >= 14
    assert len(UNRESOLVED_RELATIONSHIPS) == 6


def test_working_policy_and_scope_keep_the_imported_skill(session) -> None:
    _seed(session)
    skill = session.scalar(select(SkillArtifact).where(SkillArtifact.slug == "production-spec-qa"))
    assert skill is not None and skill.current_version_id is not None
    current = session.get(SkillVersion, skill.current_version_id)
    imported = session.scalar(
        select(SkillVersion).where(
            SkillVersion.skill_id == skill.id,
            SkillVersion.version_label == "handoff-2026-10-05",
        )
    )
    assert current is not None and imported is not None
    assert current.id != imported.id
    assert current.supersedes_version_id == imported.id
    assert EXAMPLE_BEFORE in imported.content
    assert EXAMPLE_BEFORE not in current.content
    assert imported.content.replace(EXAMPLE_BEFORE, EXAMPLE_AFTER, 1) == current.content
    snapshot = (repo_root() / "source_snapshots/2026-10-05/skills/production-spec-qa/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert EXAMPLE_BEFORE in snapshot
    money_global = session.scalar(
        select(PolicyRule).where(PolicyRule.code == "principles-a-15", PolicyRule.scope_level == "GLOBAL")
    )
    money_program = session.scalar(
        select(PolicyRule).where(PolicyRule.code == "principles-a-15", PolicyRule.scope_level == "PROGRAM")
    )
    assert money_global is not None and money_global.status == "superseded"
    assert money_program is not None and money_program.status == "active"
    assert money_program.rule_kind == "INVARIANT"
    lanes = session.scalar(select(PolicyRule).where(PolicyRule.code == "principles-c-02"))
    assert lanes is not None and lanes.status == "superseded"
    maria = session.scalar(select(PolicyRule).where(PolicyRule.code == "account-lane-maria"))
    assert maria is not None and maria.scope_level == "ACCOUNT" and maria.rule_kind == "PREFERENCE"
    ratio = session.scalar(select(PolicyRule).where(PolicyRule.code == "principles-c-04"))
    dark = session.scalar(select(PolicyRule).where(PolicyRule.code == "principles-c-07"))
    slides = session.scalars(select(PolicyRule).where(PolicyRule.status == "active")).all()
    assert ratio is not None and ratio.scope_level == "PROGRAM" and "9:19.6" in ratio.text
    assert dark is not None and dark.scope_level == "PROGRAM" and "Dark-mode" in dark.text
    assert any("three slides" in rule.text and rule.scope_level == "GLOBAL" for rule in slides)
    assert not any(rule.scope_level == "GLOBAL" and "15–20" in rule.text for rule in slides)
    active_global = [rule for rule in slides if rule.scope_level == "GLOBAL"]
    assert not any("mydashperks.com" in rule.text for rule in active_global)


def test_validation_uses_hashes_without_forcing_unknown_rights(session) -> None:
    from creative_os.models import Creative

    _seed(session)
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    assert creative is not None
    results = {name: (status, message) for name, status, message in validate_creative(session, creative)}
    assert results["provenance:Target S1 final"][0] == "PASS"
    assert results["provenance:S2 product images"][0] == "WARNING"
    assert results["rights_export:iOS26 Messages keyboard base (user's own)"][0] == "PASS"
    assert results["rights_export:Target order details base"][0] == "HUMAN_REVIEW_REQUIRED"
    assert results["aspect:Target S1 final"][0] == "PASS"
    assert results["aspect:Target S3 final"][0] == "PASS"
    assert results["aspect:2_funfetti.png"][0] == "NOT_APPLICABLE"
    assert results["aspect:slide3_birthday_camera_roll.png"][0] == "FAIL"
    assert results["lineage:Target S2 final"][0] == "PASS"
    assert results["lineage:Target S1 final"][0] == "PASS"
    assert results["lineage:Target S3 final"][0] == "HUMAN_REVIEW_REQUIRED"
    assert results["product:3_airpods4.jpg"][0] == "PASS"
    again = import_visual_supplements(session, repo_root() / "source_snapshots/supplements/2026-10-05")
    apply_preservation_baseline(session)
    session.flush()
    assert again["child_assets"] == 0
    assert again["relations"] == 0
    assert again["example_links"] == 0
    assert session.scalar(select(func.count()).select_from(StoryLockVersion)) == 1
