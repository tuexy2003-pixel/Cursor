import shutil
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from creative_os.config import repo_root
from creative_os.importers.handoff import SnapshotIntegrityError, import_handoff
from creative_os.models import (
    Account,
    ApprovalEvent,
    Asset,
    Campaign,
    CommentCluster,
    CommentDoor,
    Creative,
    CreativeGenome,
    ExperimentVariant,
    MechanicObservation,
    PerformanceSnapshot,
    PolicyRule,
    Post,
    SkillVersion,
    SourceArtifact,
    SourceSnapshot,
    StoryLockVersion,
)
from creative_os.models.entities import ImmutableVersionError
from creative_os.schemas.story_lock import LineItem
from creative_os.services.baseline import apply_preservation_baseline
from creative_os.services.consistency import ConsistencyError, resolve_post_attribution, validate_door_mapping
from creative_os.services.context_bundles import create_context_bundle
from creative_os.services.context_compiler import compile_context
from creative_os.services.lifecycle import mark_lifecycle
from creative_os.services.policy_resolver import PolicyIntegrityError, resolve_policy
from creative_os.services.story_locks import (
    StoryLockDecisionError,
    apply_story_lock_correction,
    decide_story_lock_version,
    propose_story_lock_change,
)
from creative_os.util import post_age_hours, sha256_text, utcnow
from creative_os.validation.checks import line_items_subtotal_status

pytestmark = pytest.mark.core


def _creative(session) -> Creative:
    import_handoff(session, repo_root() / "source_snapshots/2026-10-05")
    session.flush()
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    assert creative is not None
    return creative


AS_OF = datetime(2026, 10, 6, 12, 0, tzinfo=UTC)


def test_approval_transitions_state_and_stales_only_s1(session) -> None:
    creative = _creative(session)
    pointer = creative.current_approved_story_lock_version_id
    proposed = propose_story_lock_change(
        session,
        creative,
        {"floating_hook": "provider hook"},
        proposer="grok",
        reason="needs a person",
    )
    session.flush()
    assert creative.current_approved_story_lock_version_id == pointer
    assert proposed.approval_state == "PENDING"
    assert proposed.approved_by is None
    decide_story_lock_version(session, creative, proposed, "APPROVE", actor="operator", notes="human")
    session.flush()
    assert proposed.approval_state == "APPROVED"
    assert proposed.approved_by == "operator"
    assert creative.current_approved_story_lock_version_id == proposed.id
    event = session.scalar(
        select(ApprovalEvent).where(
            ApprovalEvent.version_id == proposed.id,
            ApprovalEvent.status == "APPROVED",
        )
    )
    assert event is not None
    assert event.actor == "operator"
    names = {asset.name: asset for asset in session.scalars(select(Asset)).all()}
    assert names["Target S1 final"].staleness_state == "STALE"
    for kept in (
        "Target S2 final",
        "Target S3 final",
        "Tyrel's AirPods 5 Target screenshot",
        "S2 product images",
        "AirPods 5 box photo",
    ):
        assert names[kept].stale is False


def test_reject_and_needs_changes_do_not_move_the_pointer(session) -> None:
    creative = _creative(session)
    pointer = creative.current_approved_story_lock_version_id
    rejected = propose_story_lock_change(
        session, creative, {"stakes": "no"}, proposer="grok", reason="reject me"
    )
    decide_story_lock_version(session, creative, rejected, "REJECT", actor="operator", notes=None)
    assert creative.current_approved_story_lock_version_id == pointer
    assert rejected.approval_state == "REJECTED"
    assert rejected.approved_by is None
    changes = propose_story_lock_change(
        session, creative, {"stakes": "edit"}, proposer="grok", reason="send back"
    )
    decide_story_lock_version(session, creative, changes, "NEEDS_CHANGES", actor="operator", notes="again")
    assert creative.current_approved_story_lock_version_id == pointer
    assert changes.approval_state == "NEEDS_CHANGES"


def test_outdated_proposal_requires_rebase(session) -> None:
    creative = _creative(session)
    proposed = propose_story_lock_change(
        session, creative, {"stakes": "from A"}, proposer="grok", reason="stale base"
    )
    current = apply_story_lock_correction(
        session, creative, {"reveal": "human first"}, actor="operator", reason="newer truth"
    )
    with pytest.raises(StoryLockDecisionError) as caught:
        decide_story_lock_version(session, creative, proposed, "APPROVE", actor="operator", notes=None)
    assert caught.value.code == "OUTDATED_PROPOSAL"
    assert "REBASE_REQUIRED" in str(caught.value)
    assert creative.current_approved_story_lock_version_id == current.id
    assert proposed.approval_state == "PENDING"


def test_precondition_rejects_a_moved_base(session) -> None:
    creative = _creative(session)
    seen = creative.current_approved_story_lock_version_id
    apply_story_lock_correction(session, creative, {"stakes": "moved"}, actor="operator", reason="newer")
    with pytest.raises(StoryLockDecisionError) as caught:
        apply_story_lock_correction(
            session,
            creative,
            {"reveal": "too late"},
            actor="operator",
            reason="stale editor",
            expected_current_story_lock_version_id=seen,
        )
    assert caught.value.code == "STALE_PRECONDITION"


def test_cross_creative_version_is_rejected(session) -> None:
    creative = _creative(session)
    other = session.scalar(select(Creative).where(Creative.slug == "onions-note-blank"))
    assert other is not None
    version = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    assert version is not None
    with pytest.raises(StoryLockDecisionError) as caught:
        decide_story_lock_version(session, other, version, "APPROVE", actor="operator", notes=None)
    assert caught.value.code == "CROSS_CREATIVE"
    assert other.current_approved_story_lock_version_id is None


def _writable_tree(source, destination) -> None:
    shutil.copytree(source, destination)
    destination.chmod(0o755)
    for path in destination.rglob("*"):
        path.chmod(0o755 if path.is_dir() else 0o644)


def test_snapshot_rejects_added_and_removed_paths(session, tmp_path) -> None:
    root = repo_root() / "source_snapshots/2026-10-05"
    import_handoff(session, root)
    session.flush()
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    assert creative is not None
    assert creative.account_id is None
    original_count = session.scalar(select(func.count()).select_from(SourceArtifact))
    original_root = session.scalar(select(SourceSnapshot.root_hash).where(SourceSnapshot.label == "2026-10-05"))
    added = tmp_path / "added"
    _writable_tree(root, added)
    (added / "EXTRA_NOTE.md").write_text("new path\n", encoding="utf-8")
    with pytest.raises(SnapshotIntegrityError, match="added="):
        import_handoff(session, added, snapshot_label="2026-10-05")
    removed = tmp_path / "removed"
    _writable_tree(root, removed)
    (removed / "README.md").unlink()
    with pytest.raises(SnapshotIntegrityError, match="removed="):
        import_handoff(session, removed, snapshot_label="2026-10-05")
    assert session.scalar(select(func.count()).select_from(SourceArtifact)) == original_count
    assert (
        session.scalar(select(SourceSnapshot.root_hash).where(SourceSnapshot.label == "2026-10-05"))
        == original_root
    )


def test_policy_eligibility_and_invariant_protection(session) -> None:
    creative = _creative(session)
    apply_preservation_baseline(session)
    moment = utcnow()
    pending = _policy(
        code="principles-a-01",
        scope_level="CREATIVE",
        scope_id=creative.id,
        rule_kind="INVARIANT",
        text="weaken the global rule",
        approval_state="PENDING",
    )
    future = _policy(
        code="future-pref",
        scope_level="GLOBAL",
        rule_kind="PREFERENCE",
        text="not yet",
        effective_from=moment + timedelta(days=2),
    )
    expired = _policy(
        code="expired-pref",
        scope_level="GLOBAL",
        rule_kind="PREFERENCE",
        text="over",
        effective_to=moment,
    )
    rejected = _policy(
        code="rejected-pref",
        scope_level="GLOBAL",
        rule_kind="PREFERENCE",
        text="no",
        approval_state="REJECTED",
    )
    session.add_all([pending, future, expired, rejected])
    session.flush()
    package = compile_context(session, creative, stage="full", as_of=moment, heuristic_budget=50)
    assert any(
        item["code"] == "principles-a-01" and item["scope"] == "GLOBAL" for item in package["global_invariants"]
    )
    assert all(item["code"] != "principles-a-01" for item in package["creative_locks"])
    included_codes = {item["code"] for item in package["global_invariants"] + package["program_policies"]}
    assert "future-pref" not in included_codes
    assert "expired-pref" not in included_codes
    assert "rejected-pref" not in included_codes
    global_rule = _policy(code="trust-invariant", scope_level="GLOBAL", rule_kind="INVARIANT", text="stay")
    narrower = _policy(
        code="trust-invariant",
        scope_level="CREATIVE",
        scope_id=creative.id,
        rule_kind="INVARIANT",
        text="local",
    )
    session.add_all([global_rule, narrower])
    session.flush()
    kept = resolve_policy(session, creative, moment)
    assert any(rule.id == global_rule.id for rule in kept)
    assert all(rule.id != narrower.id for rule in kept)
    mark_lifecycle(global_rule)
    global_rule.status = "superseded"
    session.flush()
    replaced = resolve_policy(session, creative, moment)
    assert any(rule.id == narrower.id for rule in replaced)
    broad = _policy(code="trust-heuristic", scope_level="GLOBAL", rule_kind="HEURISTIC", text="broad")
    specific = _policy(
        code="trust-heuristic",
        scope_level="CREATIVE",
        scope_id=creative.id,
        rule_kind="HEURISTIC",
        text="specific",
    )
    session.add_all([broad, specific])
    session.flush()
    heuristics = [rule for rule in resolve_policy(session, creative, moment) if rule.code == "trust-heuristic"]
    assert [rule.id for rule in heuristics] == [specific.id]


def test_ambiguous_policy_versions_fail(session) -> None:
    creative = _creative(session)
    session.add_all(
        [
            _policy(code="dup", scope_level="GLOBAL", rule_kind="PREFERENCE", text="one"),
            _policy(code="dup", scope_level="GLOBAL", rule_kind="PREFERENCE", text="two"),
        ]
    )
    session.flush()
    with pytest.raises(PolicyIntegrityError):
        resolve_policy(session, creative, AS_OF)


def test_skill_content_is_immutable(session) -> None:
    creative = _creative(session)
    version = session.scalars(select(SkillVersion)).first()
    assert version is not None
    original = version.content
    version_id = version.id
    nested = session.begin_nested()
    version.content = original + "\nchanged\n"
    with pytest.raises(ImmutableVersionError):
        session.flush()
    nested.rollback()
    session.expire_all()
    fresh = session.get(SkillVersion, version_id)
    assert fresh is not None
    assert fresh.content == original
    assert creative.account_id is None


def test_context_bundle_freezes_skill_content_and_as_of(session) -> None:
    creative = _creative(session)
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    assert maria is not None
    assert creative.account_id is None
    creative.account_id = maria.id
    session.add(
        MechanicObservation(
            creative_id=creative.id,
            account_id=maria.id,
            dimension="hook_pattern",
            value="recent-hook",
            observed_at=AS_OF - timedelta(days=1),
            source="test",
        )
    )
    session.add(
        MechanicObservation(
            creative_id=creative.id,
            account_id=maria.id,
            dimension="hook_pattern",
            value="future-hook",
            observed_at=AS_OF + timedelta(days=10),
            source="test",
        )
    )
    session.flush()
    first = create_context_bundle(session, creative, stage="STORY_DEVELOPMENT", as_of=AS_OF)
    second = create_context_bundle(session, creative, stage="STORY_DEVELOPMENT", as_of=AS_OF)
    assert first.payload_hash == second.payload_hash
    assert first.story_lock_version_id == creative.current_approved_story_lock_version_id
    assert first.account_dna_profile_id == maria.current_approved_dna_profile_id
    assert first.creative_genome_id == creative.current_genome_id
    assert first.as_of == AS_OF
    skills = {item["slug"]: item for item in first.compiled_payload["skill_versions"]}
    assert "story-development" in skills
    assert len(skills["story-development"]["content"]) > 80
    assert "production-spec-qa" not in skills
    lifetime = first.compiled_payload["mechanic_context"]["windows"]["lifetime"]
    values = {row["value"] for row in lifetime}
    assert "recent-hook" in values
    assert "future-hook" not in values
    apply_story_lock_correction(
        session, creative, {"floating_hook": "bundle changes"}, actor="operator", reason="new truth"
    )
    changed = create_context_bundle(session, creative, stage="STORY_DEVELOPMENT", as_of=AS_OF)
    assert changed.payload_hash != first.payload_hash
    first.compiled_text = "mutated"
    with pytest.raises(ImmutableVersionError):
        session.flush()
    session.rollback()


def test_post_attribution_and_decimal_revenue(session) -> None:
    creative = _creative(session)
    assert creative.account_id is None
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    sarah = session.scalar(select(Account).where(Account.slug == "sarah"))
    assert maria is not None and sarah is not None
    creative.account_id = maria.id
    account_id, campaign_id, genome_id = resolve_post_attribution(
        session,
        creative=creative,
        account_id=None,
        campaign_id=None,
        story_lock_version_id=creative.current_approved_story_lock_version_id,
        creative_genome_id=None,
        assets=[],
        attribution_mode="CURRENT_PUBLISH",
    )
    assert account_id == maria.id
    assert campaign_id == creative.campaign_id
    assert genome_id == creative.current_genome_id
    with pytest.raises(ConsistencyError):
        resolve_post_attribution(
            session,
            creative=creative,
            account_id=sarah.id,
            campaign_id=None,
            story_lock_version_id=creative.current_approved_story_lock_version_id,
            creative_genome_id=None,
            assets=[],
            attribution_mode="CURRENT_PUBLISH",
        )
    other = Campaign(
        program_id=creative.program_id,
        slug="other-campaign",
        name="Other",
        created_at=utcnow(),
    )
    session.add(other)
    session.flush()
    with pytest.raises(ConsistencyError):
        resolve_post_attribution(
            session,
            creative=creative,
            account_id=None,
            campaign_id=other.id,
            story_lock_version_id=creative.current_approved_story_lock_version_id,
            creative_genome_id=None,
            assets=[],
            attribution_mode="CURRENT_PUBLISH",
        )
    proposed = propose_story_lock_change(
        session, creative, {"stakes": "other lock"}, proposer="grok", reason="genome mismatch"
    )
    wrong = CreativeGenome(
        creative_id=creative.id,
        source_story_lock_version_id=proposed.id,
        version_label="wrong-lock",
        origin="HUMAN_SET",
        approval_state="APPROVED",
        created_at=utcnow(),
    )
    session.add(wrong)
    session.flush()
    with pytest.raises(ConsistencyError, match="story lock"):
        resolve_post_attribution(
            session,
            creative=creative,
            account_id=None,
            campaign_id=None,
            story_lock_version_id=creative.current_approved_story_lock_version_id,
            creative_genome_id=wrong.id,
            assets=[],
            attribution_mode="CURRENT_PUBLISH",
        )
    onions = session.scalar(select(Creative).where(Creative.slug == "onions-note-blank"))
    assert onions is not None
    foreign = CreativeGenome(
        creative_id=onions.id,
        source_story_lock_version_id=creative.current_approved_story_lock_version_id,
        version_label="other-creative",
        origin="HUMAN_SET",
        approval_state="APPROVED",
        created_at=utcnow(),
    )
    session.add(foreign)
    session.flush()
    with pytest.raises(ConsistencyError, match="different creative"):
        resolve_post_attribution(
            session,
            creative=creative,
            account_id=None,
            campaign_id=None,
            story_lock_version_id=creative.current_approved_story_lock_version_id,
            creative_genome_id=foreign.id,
            assets=[],
            attribution_mode="CURRENT_PUBLISH",
        )
    slide = session.scalar(select(Asset).where(Asset.name == "Target S1 final"))
    assert slide is not None
    slide.stale = True
    slide.staleness_state = "STALE"
    with pytest.raises(ConsistencyError, match="stale deliverable"):
        resolve_post_attribution(
            session,
            creative=creative,
            account_id=None,
            campaign_id=None,
            story_lock_version_id=creative.current_approved_story_lock_version_id,
            creative_genome_id=None,
            assets=[slide],
            attribution_mode="CURRENT_PUBLISH",
        )
    resolve_post_attribution(
        session,
        creative=creative,
        account_id=None,
        campaign_id=None,
        story_lock_version_id=creative.current_approved_story_lock_version_id,
        creative_genome_id=None,
        assets=[slide],
        attribution_mode="HISTORICAL_BACKFILL",
    )
    slide.bound_story_lock_version_id = proposed.id
    slide.stale = False
    slide.staleness_state = "CURRENT"
    with pytest.raises(ConsistencyError, match="bound to a different"):
        resolve_post_attribution(
            session,
            creative=creative,
            account_id=None,
            campaign_id=None,
            story_lock_version_id=creative.current_approved_story_lock_version_id,
            creative_genome_id=None,
            assets=[slide],
            attribution_mode="CURRENT_PUBLISH",
        )
    post = Post(
        platform="tiktok",
        published_at=utcnow() - timedelta(hours=5),
        created_at=utcnow(),
        creative_id=creative.id,
        story_lock_version_id=creative.current_approved_story_lock_version_id,
    )
    session.add(post)
    session.commit()
    fresh = Session(bind=session.get_bind())
    loaded = fresh.get(Post, post.id)
    assert loaded is not None and loaded.published_at is not None
    assert post_age_hours(loaded.published_at, utcnow()) > 4
    snap = PerformanceSnapshot(
        post_id=loaded.id,
        source="test",
        captured_at=utcnow(),
        post_age_hours=post_age_hours(loaded.published_at, utcnow()),
        revenue_amount=Decimal("19.23"),
        revenue_currency="USD",
        revenue="19.23",
    )
    fresh.add(snap)
    fresh.flush()
    assert isinstance(snap.revenue_amount, Decimal)
    assert snap.revenue_amount == Decimal("19.23")
    fresh.close()
    door = session.scalar(select(CommentDoor).limit(1))
    bare = Post(platform="tiktok", created_at=utcnow())
    session.add(bare)
    session.flush()
    cluster = CommentCluster(
        post_id=bare.id,
        label="unscoped",
        size=1,
        example_comments=[],
        unexpected=True,
        created_at=utcnow(),
    )
    session.add(cluster)
    session.flush()
    with pytest.raises(ConsistencyError, match="story lock identity"):
        validate_door_mapping(session, door, cluster)
    assert "post_id" not in ExperimentVariant.__table__.columns


def test_quantity_changes_the_subtotal() -> None:
    status, _message = line_items_subtotal_status(
        [LineItem(position=1, title="candles", quantity="2", unit_price="3")],
        "6",
    )
    assert status == "PASS"
    status, _message = line_items_subtotal_status(
        [
            LineItem(position=1, title="candles", quantity="2", unit_price="3"),
            LineItem(position=2, title="box", quantity="1", unit_price="1.50"),
        ],
        "7.50",
    )
    assert status == "PASS"
    status, message = line_items_subtotal_status(
        [LineItem(position=1, title="candles", quantity="two", unit_price="3")],
        "3",
    )
    assert status == "HUMAN_REVIEW_REQUIRED"
    assert "two" in message


def _policy(
    *,
    code: str,
    scope_level: str,
    rule_kind: str,
    text: str,
    scope_id: str | None = None,
    approval_state: str = "APPROVED",
    effective_from: datetime | None = None,
    effective_to: datetime | None = None,
) -> PolicyRule:
    return PolicyRule(
        code=code,
        scope_level=scope_level,
        scope_id=scope_id,
        rule_kind=rule_kind,
        title=text,
        text=text,
        status="active",
        content_hash=sha256_text(f"{code}|{scope_level}|{scope_id}|{text}|{approval_state}"),
        approval_state=approval_state,
        effective_from=effective_from,
        effective_to=effective_to,
        created_at=utcnow(),
    )
