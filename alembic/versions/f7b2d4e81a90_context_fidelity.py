"""Context fidelity: tasks, concepts, and nullable bundle creative.

Revision ID: f7b2d4e81a90
Revises: e1f6a2c39d55
Create Date: 2026-10-06 20:30:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f7b2d4e81a90"
down_revision: str | None = "e1f6a2c39d55"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "creative_tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("program_id", sa.String(36), sa.ForeignKey("programs.id"), nullable=False),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("campaign_id", sa.String(36), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("creative_id", sa.String(36), sa.ForeignKey("creatives.id"), nullable=True),
        sa.Column("ecosystem_id", sa.String(36), sa.ForeignKey("ecosystems.id"), nullable=True),
        sa.Column("stage", sa.String(80), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.Column("constraints", sa.JSON(), nullable=False),
        sa.Column("input_refs", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("expected_output_type", sa.String(80), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_creative_tasks_program", "creative_tasks", ["program_id", "created_at"])
    op.create_table(
        "concept_candidates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("task_id", sa.String(36), sa.ForeignKey("creative_tasks.id"), nullable=True),
        sa.Column("program_id", sa.String(36), sa.ForeignKey("programs.id"), nullable=False),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("campaign_id", sa.String(36), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("ecosystem_id", sa.String(36), sa.ForeignKey("ecosystems.id"), nullable=True),
        sa.Column("source_model_run_id", sa.String(36), nullable=True),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("premise", sa.Text(), nullable=True),
        sa.Column("family", sa.String(120), nullable=True),
        sa.Column("hook_direction", sa.Text(), nullable=True),
        sa.Column("commerce_relation", sa.String(80), nullable=True),
        sa.Column("structured_payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("created_by", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    with op.batch_alter_table("context_bundles") as batch:
        batch.alter_column("creative_id", existing_type=sa.String(36), nullable=True)
        batch.add_column(sa.Column("creative_task_id", sa.String(36), nullable=True))
        batch.create_foreign_key(
            "fk_context_bundle_task",
            "creative_tasks",
            ["creative_task_id"],
            ["id"],
        )
    op.add_column("creatives", sa.Column("selected_concept_id", sa.String(36), nullable=True))
    with op.batch_alter_table("creatives") as batch:
        batch.create_foreign_key(
            "fk_creative_selected_concept",
            "concept_candidates",
            ["selected_concept_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("creatives") as batch:
        batch.drop_constraint("fk_creative_selected_concept", type_="foreignkey")
    op.drop_column("creatives", "selected_concept_id")
    with op.batch_alter_table("context_bundles") as batch:
        batch.drop_constraint("fk_context_bundle_task", type_="foreignkey")
        batch.drop_column("creative_task_id")
        batch.alter_column("creative_id", existing_type=sa.String(36), nullable=False)
    op.drop_table("concept_candidates")
    op.drop_index("ix_creative_tasks_program", table_name="creative_tasks")
    op.drop_table("creative_tasks")
