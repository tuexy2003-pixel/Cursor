"""Core integrity: snapshots, hashes, bindings, and indexes.

Revision ID: c8d4e1a07b33
Revises: b7c1a9e0d4f2
Create Date: 2026-10-06 18:20:00
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

from creative_os.services.canonical import document_hash

revision: str = "c8d4e1a07b33"
down_revision: str | None = "b7c1a9e0d4f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SNAPSHOT_ID = "11111111-1111-4111-8111-111111111111"


def upgrade() -> None:
    op.create_table(
        "source_snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("label", sa.String(160), nullable=False, unique=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("root_hash", sa.String(64), nullable=True),
        sa.Column("source_description", sa.Text(), nullable=True),
        sa.Column("immutable", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.bulk_insert(
        sa.table(
            "source_snapshots",
            sa.column("id", sa.String),
            sa.column("label", sa.String),
            sa.column("captured_at", sa.DateTime),
            sa.column("root_hash", sa.String),
            sa.column("source_description", sa.Text),
            sa.column("immutable", sa.Boolean),
            sa.column("created_at", sa.DateTime),
        ),
        [
            {
                "id": SNAPSHOT_ID,
                "label": "2026-10-05",
                "captured_at": None,
                "root_hash": None,
                "source_description": "Backfilled from the preservation baseline import.",
                "immutable": True,
                "created_at": datetime.now(UTC),
            }
        ],
    )
    op.create_table(
        "source_artifacts_next",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("snapshot_id", sa.String(36), sa.ForeignKey("source_snapshots.id"), nullable=False),
        sa.Column("relative_path", sa.Text(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("snapshot_id", "relative_path", name="uq_source_artifact_snapshot_path"),
    )
    op.execute(
        sa.text(
            "INSERT INTO source_artifacts_next "
            "(id, snapshot_id, relative_path, sha256, size_bytes, kind, imported_at) "
            "SELECT id, :snapshot_id, relative_path, sha256, size_bytes, kind, imported_at "
            "FROM source_artifacts"
        ).bindparams(snapshot_id=SNAPSHOT_ID)
    )
    op.drop_table("source_artifacts")
    op.rename_table("source_artifacts_next", "source_artifacts")

    _add("story_lock_versions", sa.Column("document_hash", sa.String(64), nullable=True))
    _add(
        "story_lock_versions",
        sa.Column("approval_state", sa.String(40), nullable=False, server_default="APPROVED"),
    )
    _backfill_document_hashes()
    _add("accounts", sa.Column("current_approved_dna_profile_id", sa.String(36), nullable=True))
    _add("creatives", sa.Column("current_genome_id", sa.String(36), nullable=True))
    _add("policy_rules", sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True))
    _add("policy_rules", sa.Column("supersedes_rule_id", sa.String(36), nullable=True))
    _add("policy_rules", sa.Column("source_skill_version_id", sa.String(36), nullable=True))
    _add("policy_rules", sa.Column("source_artifact_id", sa.String(36), nullable=True))
    _add(
        "policy_rules",
        sa.Column("approval_state", sa.String(40), nullable=False, server_default="APPROVED"),
    )
    _add(
        "assets",
        sa.Column("staleness_state", sa.String(40), nullable=False, server_default="CURRENT"),
    )
    op.execute("UPDATE assets SET staleness_state = 'STALE' WHERE stale")
    _add(
        "stale_artifact_records",
        sa.Column("staleness_state", sa.String(40), nullable=False, server_default="STALE"),
    )
    _add("creative_genomes", sa.Column("source_story_lock_version_id", sa.String(36), nullable=True))
    _add(
        "creative_genomes",
        sa.Column("origin", sa.String(40), nullable=False, server_default="HUMAN_SET"),
    )
    _add(
        "creative_genomes",
        sa.Column("approval_state", sa.String(40), nullable=False, server_default="APPROVED"),
    )
    _add("creative_genomes", sa.Column("confidence", sa.Numeric(4, 3), nullable=True))
    _add("creative_genomes", sa.Column("source_run_id", sa.String(36), nullable=True))
    _add(
        "account_dna_profiles",
        sa.Column("approval_state", sa.String(40), nullable=False, server_default="APPROVED"),
    )
    _add(
        "account_dna_profiles",
        sa.Column("origin", sa.String(40), nullable=False, server_default="HUMAN_SET"),
    )
    _add(
        "experiments",
        sa.Column("mode", sa.String(40), nullable=False, server_default="SINGLE_VARIABLE"),
    )
    _add(
        "experiments",
        sa.Column("changed_dimensions", sa.JSON(), nullable=False, server_default="[]"),
    )
    _add("posts", sa.Column("story_lock_version_id", sa.String(36), nullable=True))
    _add("posts", sa.Column("creative_genome_id", sa.String(36), nullable=True))
    _add("posts", sa.Column("experiment_variant_id", sa.String(36), nullable=True))
    _add("performance_snapshots", sa.Column("revenue_amount", sa.Numeric(12, 2), nullable=True))
    _add("performance_snapshots", sa.Column("revenue_currency", sa.String(8), nullable=True))
    _add("mechanic_observations", sa.Column("account_id", sa.String(36), nullable=True))
    _add("mechanic_observations", sa.Column("post_id", sa.String(36), nullable=True))
    _add("mechanic_observations", sa.Column("story_lock_version_id", sa.String(36), nullable=True))
    _add("mechanic_observations", sa.Column("genome_id", sa.String(36), nullable=True))

    op.execute(
        """
        UPDATE creative_genomes
        SET source_story_lock_version_id = (
            SELECT current_approved_story_lock_version_id
            FROM creatives
            WHERE creatives.id = creative_genomes.creative_id
        )
        WHERE source_story_lock_version_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE creatives
        SET current_genome_id = (
            SELECT id FROM creative_genomes
            WHERE creative_genomes.creative_id = creatives.id
            ORDER BY created_at
            LIMIT 1
        )
        WHERE current_genome_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE accounts
        SET current_approved_dna_profile_id = (
            SELECT id FROM account_dna_profiles
            WHERE account_dna_profiles.account_id = accounts.id
            AND version_number = 1
        )
        WHERE current_approved_dna_profile_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE mechanic_observations
        SET account_id = (
            SELECT account_id FROM creatives
            WHERE creatives.id = mechanic_observations.creative_id
        )
        WHERE account_id IS NULL
        """
    )

    op.create_table(
        "asset_lock_dependencies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("asset_id", sa.String(36), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("creative_id", sa.String(36), sa.ForeignKey("creatives.id"), nullable=True),
        sa.Column("field_path", sa.String(240), nullable=False),
        sa.Column("slide_index", sa.Integer(), nullable=True),
        sa.Column("dependency_kind", sa.String(40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("explicit", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("asset_id", "field_path", name="uq_asset_lock_dependency"),
    )
    _backfill_known_dependencies()
    op.create_table(
        "post_assets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("post_id", sa.String(36), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("asset_id", sa.String(36), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("slide_index", sa.Integer(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("role", sa.String(40), nullable=True),
        sa.UniqueConstraint("post_id", "asset_id", "slide_index", name="uq_post_asset_slide"),
    )
    op.create_table(
        "experiment_variant_posts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("variant_id", sa.String(36), sa.ForeignKey("experiment_variants.id"), nullable=False),
        sa.Column("post_id", sa.String(36), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("variant_id", "post_id", name="uq_variant_post"),
    )
    op.create_table(
        "comment_cluster_members",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("cluster_id", sa.String(36), sa.ForeignKey("comment_clusters.id"), nullable=False),
        sa.Column("comment_id", sa.String(36), sa.ForeignKey("comments.id"), nullable=False),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("assigned_by", sa.String(160), nullable=True),
        sa.Column("human_override", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("cluster_id", "comment_id", name="uq_cluster_comment"),
    )

    _fk(
        "story_lock_versions",
        "fk_story_lock_version_supersedes",
        "story_lock_versions",
        ["supersedes_version_id"],
    )
    _fk("skill_versions", "fk_skill_version_supersedes", "skill_versions", ["supersedes_version_id"])
    _fk("account_dna_profiles", "fk_dna_profile_supersedes", "account_dna_profiles", ["supersedes_profile_id"])
    _fk(
        "stale_artifact_records",
        "fk_stale_record_superseded_by",
        "story_lock_versions",
        ["superseded_by_version_id"],
    )
    _fk("experiment_variants", "fk_experiment_variant_post", "posts", ["post_id"])
    _fk("accounts", "fk_account_current_dna", "account_dna_profiles", ["current_approved_dna_profile_id"])
    _fk("creatives", "fk_creative_current_genome", "creative_genomes", ["current_genome_id"])
    _fk("policy_rules", "fk_policy_supersedes", "policy_rules", ["supersedes_rule_id"])
    _fk("policy_rules", "fk_policy_skill_version", "skill_versions", ["source_skill_version_id"])
    _fk("policy_rules", "fk_policy_source_artifact", "source_artifacts", ["source_artifact_id"])
    _fk("posts", "fk_post_story_lock", "story_lock_versions", ["story_lock_version_id"])
    _fk("posts", "fk_post_genome", "creative_genomes", ["creative_genome_id"])
    _fk("posts", "fk_post_experiment_variant", "experiment_variants", ["experiment_variant_id"])
    _fk("mechanic_observations", "fk_mechanic_account", "accounts", ["account_id"])
    _fk("mechanic_observations", "fk_mechanic_post", "posts", ["post_id"])
    _fk("mechanic_observations", "fk_mechanic_lock", "story_lock_versions", ["story_lock_version_id"])
    _fk("mechanic_observations", "fk_mechanic_genome", "creative_genomes", ["genome_id"])
    _fk("creative_genomes", "fk_genome_story_lock", "story_lock_versions", ["source_story_lock_version_id"])

    op.create_index("ix_comments_post_id", "comments", ["post_id"])
    op.create_index("ix_performance_post_captured", "performance_snapshots", ["post_id", "captured_at"])
    op.create_index("ix_posts_account_published", "posts", ["account_id", "published_at"])
    op.create_index("ix_posts_creative_id", "posts", ["creative_id"])
    op.create_index("ix_assets_creative_id", "assets", ["creative_id"])
    op.create_index("ix_assets_bound_story_lock_version_id", "assets", ["bound_story_lock_version_id"])
    op.create_index("ix_story_line_items_version", "story_line_items", ["story_lock_version_id"])
    op.create_index("ix_slide_projections_version", "slide_projections", ["story_lock_version_id"])
    op.create_index("ix_comment_doors_creative_lock", "comment_doors", ["creative_id", "story_lock_version_id"])
    op.create_index(
        "ix_mechanics_account_dimension_time",
        "mechanic_observations",
        ["account_id", "dimension", "observed_at"],
    )
    op.create_index("ix_genome_facets_genome_dimension", "genome_facets", ["genome_id", "dimension"])
    op.create_index("ix_account_dna_observations_profile", "account_dna_observations", ["profile_id"])


def downgrade() -> None:
    for name in (
        "ix_account_dna_observations_profile",
        "ix_genome_facets_genome_dimension",
        "ix_mechanics_account_dimension_time",
        "ix_comment_doors_creative_lock",
        "ix_slide_projections_version",
        "ix_story_line_items_version",
        "ix_assets_bound_story_lock_version_id",
        "ix_assets_creative_id",
        "ix_posts_creative_id",
        "ix_posts_account_published",
        "ix_performance_post_captured",
        "ix_comments_post_id",
    ):
        op.drop_index(name)
    op.drop_table("comment_cluster_members")
    op.drop_table("experiment_variant_posts")
    op.drop_table("post_assets")
    op.drop_table("asset_lock_dependencies")
    op.create_table(
        "source_artifacts_prev",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("relative_path", sa.Text(), nullable=False, unique=True),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.execute(
        "INSERT INTO source_artifacts_prev (id, relative_path, sha256, size_bytes, kind, imported_at) "
        "SELECT id, relative_path, sha256, size_bytes, kind, imported_at FROM source_artifacts"
    )
    op.drop_table("source_artifacts")
    op.rename_table("source_artifacts_prev", "source_artifacts")
    op.drop_table("source_snapshots")


def _add(table: str, column: sa.Column) -> None:
    op.add_column(table, column)


def _fk(table: str, name: str, target: str, columns: list[str]) -> None:
    with op.batch_alter_table(table) as batch:
        batch.create_foreign_key(name, target, columns, ["id"])


def _backfill_document_hashes() -> None:
    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, content_json FROM story_lock_versions")).fetchall()
    for row in rows:
        payload = row.content_json
        if isinstance(payload, str):
            payload = json.loads(payload)
        digest = document_hash(payload)
        connection.execute(
            sa.text("UPDATE story_lock_versions SET document_hash = :digest WHERE id = :id"),
            {"digest": digest, "id": row.id},
        )


def _backfill_known_dependencies() -> None:
    from uuid import uuid4

    from creative_os.services.dependencies import KNOWN_DEPENDENCIES

    connection = op.get_bind()
    notes = "Explicit handoff dependency. Not inferred from a shared story-lock binding."
    for name, specs in KNOWN_DEPENDENCIES.items():
        assets = connection.execute(
            sa.text("SELECT id, creative_id FROM assets WHERE name = :name"),
            {"name": name},
        ).fetchall()
        for asset in assets:
            for field_path, slide_index in specs:
                existing = connection.execute(
                    sa.text(
                        "SELECT 1 FROM asset_lock_dependencies "
                        "WHERE asset_id = :asset_id AND field_path = :field_path"
                    ),
                    {"asset_id": asset.id, "field_path": field_path},
                ).first()
                if existing:
                    continue
                connection.execute(
                    sa.text(
                        "INSERT INTO asset_lock_dependencies "
                        "(id, asset_id, creative_id, field_path, slide_index, "
                        "dependency_kind, notes, explicit) "
                        "VALUES (:id, :asset_id, :creative_id, :field_path, :slide_index, "
                        "'FIELD', :notes, 1)"
                    ),
                    {
                        "id": str(uuid4()),
                        "asset_id": asset.id,
                        "creative_id": asset.creative_id,
                        "field_path": field_path,
                        "slide_index": slide_index,
                        "notes": notes,
                    },
                )
