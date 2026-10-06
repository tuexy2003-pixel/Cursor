import shutil

import pytest
from sqlalchemy import func, select

from creative_os.config import repo_root
from creative_os.importers.handoff import SnapshotIntegrityError, import_handoff
from creative_os.models import (
    Account,
    AccountDnaProfile,
    Asset,
    Comment,
    CommentClusterMember,
    CommentDoor,
    Creative,
    CreativeGenome,
    ExperimentVariant,
    Post,
    PostAsset,
    SourceArtifact,
    SourceSnapshot,
    StoryLockVersion,
)
from creative_os.schemas.story_lock import FieldPatch, StoryLockDocument
from creative_os.services.baseline import apply_preservation_baseline
from creative_os.services.canonical import document_hash
from creative_os.services.context_compiler import compile_context
from creative_os.services.diff import deep_diff
from creative_os.services.experiments import validate_experiment_isolation
from creative_os.services.story_lock_render import parse_canonical_markdown, render_canonical_markdown
from creative_os.services.story_locks import (
    apply_story_lock_correction,
    build_document,
    decide_story_lock_version,
    propose_story_lock_change,
)
from creative_os.util import utcnow

pytestmark = pytest.mark.core


def _creative(session) -> Creative:
    import_handoff(session, repo_root() / "source_snapshots/2026-10-05")
    session.flush()
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    assert creative is not None
    return creative


def _document(session, creative: Creative) -> StoryLockDocument:
    version = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    assert version is not None
    return StoryLockDocument.model_validate(version.content_json)


def test_commerce_relation_changes_canonical_hash() -> None:
    document = StoryLockDocument(title="Example", commerce_relation="order is the proof")
    changed = document.model_copy(update={"commerce_relation": "order is the cover"})
    changed = StoryLockDocument.model_validate(changed.model_dump())
    assert document_hash(document) != document_hash(changed)


def test_continuity_changes_canonical_hash() -> None:
    document = StoryLockDocument(title="Example", continuity=[])
    changed = build_document(
        document,
        {},
        [FieldPatch(path="/continuity", value=[{"slide_index": 1, "field": "clock", "value": "4:15 PM"}])],
    )
    assert document_hash(document) != document_hash(changed)


def test_boolean_story_date_is_rejected() -> None:
    document = StoryLockDocument(title="Example", story_date="2026-10-05")
    with pytest.raises(ValueError, match="validation failed"):
        build_document(document, {"story_date": True}, [])


def test_canonical_markdown_round_trip() -> None:
    document = StoryLockDocument(
        title="Round trip",
        core_story="Sister hides the order.",
        hook="don't look",
        floating_hook="my birthday is literally today 😭",
        stakes="today",
        trigger="the text",
        action="she opens it",
        expected_next_beat="what's in it",
        reveal="AirPods",
        commerce_relation="the order is the reveal",
        story_works_without_economics=True,
        dialogue=[{"speaker": "sister", "direction": "incoming", "text": "chore stuff"}],
        line_items=[
            {
                "position": 3,
                "title": "Apple AirPods 5",
                "quantity": "1",
                "model": "AirPods 5",
                "generation": "5",
                "variant": "wireless",
            }
        ],
        economics={"subtotal": "142.97", "discount": "125.00", "tax": "1.26", "total": "19.23"},
        story_date="2026-10-05",
        story_weekday="Monday",
        slides=[{"index": 1, "visible_clock": "4:14 PM", "overlay": "today"}],
        continuity=[{"slide_index": 1, "field": "clock", "value": "4:14 PM"}],
        comment_doors=[{"kind": "primary", "text": "the airpods"}],
        viral_texture=[{"slide_index": 3, "text": "box at the edge", "category": "object"}],
        stale_notes=["v1 used tomorrow"],
        extra={"note": "kept"},
    )
    rendered = render_canonical_markdown(document)
    assert "COMMERCE RELATION:" in rendered
    assert "CONTINUITY:" in rendered
    assert "VIRAL TEXTURE:" in rendered
    assert parse_canonical_markdown(rendered).model_dump() == document.model_dump()


def test_deep_diff_reports_only_floating_hook(session) -> None:
    creative = _creative(session)
    original = _document(session, creative)
    updated = apply_story_lock_correction(
        session,
        creative,
        {"floating_hook": "my birthday is literally tonight 😭"},
        actor="Tyrel",
        reason="diff fixture",
    )
    paths = deep_diff(original.model_dump(mode="json"), updated.content_json)
    assert [row["path"] for row in paths] == ["/floating_hook"]


def test_floating_hook_stales_only_s1(session) -> None:
    creative = _creative(session)
    apply_story_lock_correction(
        session,
        creative,
        {"floating_hook": "my birthday is literally tonight 😭"},
        actor="Tyrel",
        reason="hook only",
    )
    session.flush()
    names = {asset.name: asset for asset in session.scalars(select(Asset)).all()}
    assert names["Target S1 final"].staleness_state == "STALE"
    for kept in (
        "Target S2 final",
        "Target S3 final",
        "Target order details base",
        "S2 product images",
        "AirPods 5 box photo",
    ):
        assert names[kept].stale is False


def test_airpods_model_stales_s2_and_s3_not_s1(session) -> None:
    creative = _creative(session)
    apply_story_lock_correction(
        session,
        creative,
        {},
        actor="Tyrel",
        reason="product only",
        patches=[FieldPatch(path="/line_items/2/model", value="AirPods 6")],
    )
    session.flush()
    names = {
        asset.name: asset
        for asset in session.scalars(select(Asset).where(Asset.creative_id == creative.id)).all()
    }
    assert names["Target S1 final"].stale is False
    assert names["Target S2 final"].staleness_state == "STALE"
    assert names["Target S3 final"].staleness_state == "STALE"
    assert names["AirPods 5 box photo"].stale is False


def test_provider_proposal_cannot_move_the_pointer(session) -> None:
    creative = _creative(session)
    pointer = creative.current_approved_story_lock_version_id
    proposed = propose_story_lock_change(
        session,
        creative,
        {"commerce_relation": "provider guess"},
        proposer="grok",
        reason="model proposal",
    )
    session.flush()
    assert creative.current_approved_story_lock_version_id == pointer
    assert proposed.approval_state == "PENDING"
    assert proposed.id != pointer
    claimed = propose_story_lock_change(
        session,
        creative,
        {"stakes": "provider"},
        proposer="operator",
        reason="proposer string is not an approval",
    )
    assert creative.current_approved_story_lock_version_id == pointer
    assert claimed.approval_state == "PENDING"


def test_human_approval_moves_the_pointer(session) -> None:
    creative = _creative(session)
    pointer = creative.current_approved_story_lock_version_id
    proposed = propose_story_lock_change(
        session,
        creative,
        {"stakes": "birthday today"},
        proposer="grok",
        reason="needs a person",
    )
    decide_story_lock_version(session, creative, proposed, "APPROVE", actor="operator", notes="human")
    session.flush()
    assert creative.current_approved_story_lock_version_id == proposed.id
    assert creative.current_approved_story_lock_version_id != pointer


def test_new_snapshot_does_not_rewrite_the_old_one(session, tmp_path) -> None:
    root = repo_root() / "source_snapshots/2026-10-05"
    import_handoff(session, root)
    session.flush()
    original = session.scalar(select(SourceArtifact).where(SourceArtifact.relative_path == "README.md"))
    assert original is not None
    original_hash = original.sha256
    clone = tmp_path / "2026-10-06"
    shutil.copytree(root, clone)
    readme = clone / "README.md"
    readme.chmod(0o644)
    readme.write_text(readme.read_text(encoding="utf-8") + "\nnext handoff\n", encoding="utf-8")
    import_handoff(session, clone, snapshot_label="2026-10-06")
    session.flush()
    rows = session.scalars(select(SourceArtifact).where(SourceArtifact.relative_path == "README.md")).all()
    assert len(rows) == 2
    assert {row.snapshot_id for row in rows}.__len__() == 2
    assert original.sha256 == original_hash
    assert session.scalar(select(func.count()).select_from(SourceSnapshot)) == 2


def test_same_snapshot_rejects_changed_bytes(session, tmp_path) -> None:
    root = repo_root() / "source_snapshots/2026-10-05"
    import_handoff(session, root)
    session.flush()
    clone = tmp_path / "2026-10-05"
    shutil.copytree(root, clone)
    readme = clone / "README.md"
    readme.chmod(0o644)
    readme.write_text(readme.read_text(encoding="utf-8") + "\nmutated\n", encoding="utf-8")
    with pytest.raises(SnapshotIntegrityError):
        import_handoff(session, clone, snapshot_label="2026-10-05")


def test_context_keeps_invariants_under_a_tight_budget(session) -> None:
    creative = _creative(session)
    apply_preservation_baseline(session)
    session.flush()
    package = compile_context(session, creative, stage="production", heuristic_budget=0)
    assert package["provider_execution"] == "NOT_IMPLEMENTED"
    assert package["global_invariants"]
    assert all(item["rule_kind"] == "INVARIANT" for item in package["global_invariants"])
    excluded_codes = {item.get("code") for item in package["excluded_for_token_budget"]}
    invariant_codes = {item["code"] for item in package["global_invariants"]}
    assert excluded_codes.isdisjoint(invariant_codes)
    assert package["account_policies"] == []
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    assert maria is not None
    creative.account_id = maria.id
    scoped = compile_context(session, creative, stage="full", heuristic_budget=50)
    assert any(item["code"].startswith("account-lane-") for item in scoped["account_policies"])
    assert scoped["creative_locks"]
    assert scoped["current_story_lock_version"]["version_number"] == 1


def test_unapproved_dna_is_not_current(session) -> None:
    creative = _creative(session)
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    assert maria is not None
    assert maria.current_approved_dna_profile_id is not None
    draft = AccountDnaProfile(
        account_id=maria.id,
        version_number=2,
        supersedes_profile_id=maria.current_approved_dna_profile_id,
        approval_state="PENDING",
        origin="MODEL_INFERRED",
        created_at=utcnow(),
    )
    session.add(draft)
    session.flush()
    current = session.get(AccountDnaProfile, maria.current_approved_dna_profile_id)
    assert current is not None
    assert current.version_number == 1
    assert current.approval_state == "APPROVED"
    assert draft.version_number > current.version_number
    creative.account_id = maria.id
    package = compile_context(session, creative, stage="full", heuristic_budget=50)
    assert package["account_dna"]["profile_id"] == current.id


def test_genome_is_bound_to_the_story_lock(session) -> None:
    creative = _creative(session)
    genome = session.get(CreativeGenome, creative.current_genome_id)
    assert genome is not None
    assert genome.source_story_lock_version_id == creative.current_approved_story_lock_version_id
    assert genome.origin == "HUMAN_SET"
    proposed = propose_story_lock_change(
        session,
        creative,
        {"stakes": "later"},
        proposer="grok",
        reason="does not retarget the genome",
    )
    session.flush()
    assert genome.source_story_lock_version_id != proposed.id


def test_post_keeps_its_original_lock_and_assets(session) -> None:
    creative = _creative(session)
    original = creative.current_approved_story_lock_version_id
    slide = session.scalar(select(Asset).where(Asset.name == "Target S1 final"))
    assert slide is not None
    from creative_os.services.consistency import validate_post

    post = Post(
        creative_id=creative.id,
        account_id=None,
        platform="tiktok",
        story_lock_version_id=original,
        creative_genome_id=creative.current_genome_id,
        published_at=utcnow(),
        created_at=utcnow(),
    )
    session.add(post)
    session.flush()
    session.add(PostAsset(post_id=post.id, asset_id=slide.id, slide_index=0, sort_order=0, role="EXAMPLE"))
    apply_story_lock_correction(
        session,
        creative,
        {"floating_hook": "my birthday is literally tonight 😭"},
        actor="Tyrel",
        reason="later correction",
    )
    session.flush()
    session.refresh(post)
    assert post.story_lock_version_id == original
    assert creative.current_approved_story_lock_version_id != original
    linked = session.scalar(select(PostAsset).where(PostAsset.post_id == post.id))
    assert linked is not None and linked.asset_id == slide.id
    validate_post(
        session,
        creative=creative,
        account=None,
        campaign=None,
        story_lock=session.get(StoryLockVersion, original),
        variant=None,
        assets=[slide],
    )


def test_post_rejects_cross_account_assignment(session) -> None:
    creative = _creative(session)
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    sarah = session.scalar(select(Account).where(Account.slug == "sarah"))
    assert maria is not None and sarah is not None
    creative.account_id = maria.id
    from creative_os.services.consistency import ConsistencyError, validate_post

    with pytest.raises(ConsistencyError, match="account"):
        validate_post(
            session,
            creative=creative,
            account=sarah,
            campaign=None,
            story_lock=None,
            variant=None,
            assets=[],
        )


def test_single_variable_experiment_rejects_a_second_dimension() -> None:
    with pytest.raises(ValueError, match="single-variable"):
        validate_experiment_isolation(
            mode="SINGLE_VARIABLE",
            variable_dimension="floating_hook",
            control={"floating_hook": "today", "dialogue": "old"},
            variant={"floating_hook": "tonight", "dialogue": "new"},
        )
    changed = validate_experiment_isolation(
        mode="MULTIVARIATE",
        variable_dimension="floating_hook",
        control={"floating_hook": "today", "dialogue": "old"},
        variant={"floating_hook": "tonight", "dialogue": "new"},
    )
    assert changed == ["dialogue", "floating_hook"]


def test_cluster_members_and_cross_creative_door(session) -> None:
    creative = _creative(session)
    other = session.scalar(select(Creative).where(Creative.slug != creative.slug))
    assert other is not None
    post = Post(creative_id=creative.id, platform="tiktok", created_at=utcnow())
    session.add(post)
    session.flush()
    comment = Comment(post_id=post.id, body="the airpods??", created_at=utcnow())
    session.add(comment)
    session.flush()
    from creative_os.models import CommentCluster
    from creative_os.services.consistency import (
        ConsistencyError,
        validate_cluster_comments,
        validate_door_mapping,
    )

    cluster = CommentCluster(
        post_id=post.id,
        label="airpods",
        size=1,
        example_comments=[],
        unexpected=False,
        created_at=utcnow(),
    )
    session.add(cluster)
    session.flush()
    members = validate_cluster_comments(session, post.id, [comment.id])
    session.add(
        CommentClusterMember(
            cluster_id=cluster.id,
            comment_id=members[0].id,
            assigned_by="operator",
            human_override=False,
            created_at=utcnow(),
        )
    )
    session.flush()
    assert session.scalar(select(func.count()).select_from(CommentClusterMember)) == 1
    door = session.scalar(select(CommentDoor).where(CommentDoor.creative_id == other.id))
    if door is None:
        door = CommentDoor(creative_id=other.id, kind="primary", text="unrelated", story_lock_version_id=None)
        session.add(door)
        session.flush()
    with pytest.raises(ConsistencyError, match="different creative"):
        validate_door_mapping(session, door, cluster)


def test_variant_can_have_more_than_one_post(session) -> None:
    creative = _creative(session)
    from creative_os.models import Experiment, ExperimentVariantPost

    experiment = Experiment(
        name="hook",
        hypothesis="tonight vs today",
        creative_id=creative.id,
        variable_dimension="floating_hook",
        mode="SINGLE_VARIABLE",
        changed_dimensions=["floating_hook"],
        secondary_metrics=[],
        status="draft",
        created_at=utcnow(),
    )
    session.add(experiment)
    session.flush()
    variant = ExperimentVariant(
        experiment_id=experiment.id,
        name="treatment",
        is_control=False,
        changes={"floating_hook": "tonight"},
        fixed={},
    )
    session.add(variant)
    session.flush()
    for _ in range(2):
        post = Post(
            creative_id=creative.id,
            platform="tiktok",
            experiment_variant_id=variant.id,
            story_lock_version_id=creative.current_approved_story_lock_version_id,
            created_at=utcnow(),
        )
        session.add(post)
        session.flush()
        session.add(ExperimentVariantPost(variant_id=variant.id, post_id=post.id, created_at=utcnow()))
    session.flush()
    assert session.scalar(select(func.count()).select_from(ExperimentVariantPost)) == 2
