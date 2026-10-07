"""Trust, attribution, and context bundles.

Revision ID: e1f6a2c39d55
Revises: c8d4e1a07b33
Create Date: 2026-10-06 19:30:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e1f6a2c39d55"
down_revision: str | None = "c8d4e1a07b33"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "context_bundles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("creative_id", sa.String(36), sa.ForeignKey("creatives.id"), nullable=False),
        sa.Column("requested_stage", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("story_lock_version_id", sa.String(36), nullable=True),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("campaign_id", sa.String(36), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column(
            "account_dna_profile_id",
            sa.String(36),
            sa.ForeignKey("account_dna_profiles.id"),
            nullable=True,
        ),
        sa.Column("creative_genome_id", sa.String(36), sa.ForeignKey("creative_genomes.id"), nullable=True),
        sa.Column("policy_rule_ids", sa.JSON(), nullable=False),
        sa.Column("skill_version_ids", sa.JSON(), nullable=False),
        sa.Column("benchmark_ids", sa.JSON(), nullable=False),
        sa.Column("reference_ids", sa.JSON(), nullable=False),
        sa.Column("mechanic_as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("compiled_payload", sa.JSON(), nullable=False),
        sa.Column("compiled_text", sa.Text(), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("compiler_version", sa.String(40), nullable=False),
        sa.Column("size_estimate", sa.Integer(), nullable=False),
        sa.Column("token_estimate", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
    )
    op.create_index("ix_context_bundles_creative", "context_bundles", ["creative_id", "created_at"])
    with op.batch_alter_table("context_bundles") as batch:
        batch.create_foreign_key(
            "fk_context_bundle_story_lock",
            "story_lock_versions",
            ["story_lock_version_id"],
            ["id"],
        )
    op.add_column("model_runs", sa.Column("context_bundle_id", sa.String(36), nullable=True))
    op.add_column("posts", sa.Column("campaign_id", sa.String(36), nullable=True))
    with op.batch_alter_table("model_runs") as batch:
        batch.create_foreign_key(
            "fk_model_run_context_bundle",
            "context_bundles",
            ["context_bundle_id"],
            ["id"],
        )
    with op.batch_alter_table("posts") as batch:
        batch.create_foreign_key("fk_post_campaign", "campaigns", ["campaign_id"], ["id"])
    op.create_index("ix_posts_campaign_id", "posts", ["campaign_id"])
    with op.batch_alter_table("experiment_variants") as batch:
        batch.drop_constraint("fk_experiment_variant_post", type_="foreignkey")
        batch.drop_column("post_id")


def downgrade() -> None:
    with op.batch_alter_table("experiment_variants") as batch:
        batch.add_column(sa.Column("post_id", sa.String(36), nullable=True))
        batch.create_foreign_key("fk_experiment_variant_post", "posts", ["post_id"], ["id"])
    op.drop_index("ix_posts_campaign_id", table_name="posts")
    with op.batch_alter_table("posts") as batch:
        batch.drop_constraint("fk_post_campaign", type_="foreignkey")
    op.drop_column("posts", "campaign_id")
    with op.batch_alter_table("model_runs") as batch:
        batch.drop_constraint("fk_model_run_context_bundle", type_="foreignkey")
    op.drop_column("model_runs", "context_bundle_id")
    op.drop_index("ix_context_bundles_creative", table_name="context_bundles")
    op.drop_table("context_bundles")
