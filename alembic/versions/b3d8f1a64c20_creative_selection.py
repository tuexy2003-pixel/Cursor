"""Creative selection: batches, manual evaluations, and text-run binding.

Revision ID: b3d8f1a64c20
Revises: f7b2d4e81a90
Create Date: 2026-10-06 21:10:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b3d8f1a64c20"
down_revision: str | None = "f7b2d4e81a90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "concept_batches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("task_id", sa.String(36), sa.ForeignKey("creative_tasks.id"), nullable=True),
        sa.Column("source_model_run_id", sa.String(36), sa.ForeignKey("model_runs.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("diversity_level", sa.String(20), nullable=True),
        sa.Column("diversity_report", sa.JSON(), nullable=False),
    )
    op.create_table(
        "manual_evaluations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("origin", sa.String(80), nullable=False),
        sa.Column("provider_name", sa.String(80), nullable=False),
        sa.Column("model_name", sa.String(160), nullable=False),
        sa.Column("packet_hash", sa.String(64), nullable=False),
        sa.Column("recorded_context_bundle_id", sa.String(36), nullable=True),
        sa.Column("recorded_task_id", sa.String(36), nullable=True),
        sa.Column("stage", sa.String(80), nullable=False),
        sa.Column("task_instruction", sa.Text(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
        sa.Column("rubric_score", sa.String(40), nullable=False),
        sa.Column("rubric_item_scores", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("run_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_path", sa.Text(), nullable=True),
        sa.UniqueConstraint(
            "provider_name",
            "model_name",
            "packet_hash",
            "stage",
            name="uq_manual_evaluation",
        ),
    )
    op.create_table(
        "story_audit_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("model_run_id", sa.String(36), sa.ForeignKey("model_runs.id"), nullable=False),
        sa.Column("context_bundle_id", sa.String(36), sa.ForeignKey("context_bundles.id"), nullable=False),
        sa.Column("creative_id", sa.String(36), sa.ForeignKey("creatives.id"), nullable=True),
        sa.Column("overall_status", sa.String(40), nullable=False),
        sa.Column("diagnosis", sa.Text(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("record_status", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    with op.batch_alter_table("concept_candidates") as batch:
        batch.add_column(sa.Column("batch_id", sa.String(36), nullable=True))
        batch.add_column(sa.Column("mechanism_fingerprint", sa.JSON(), nullable=False, server_default="{}"))
        batch.create_foreign_key("fk_concept_batch", "concept_batches", ["batch_id"], ["id"])
    with op.batch_alter_table("model_runs") as batch:
        batch.add_column(sa.Column("creative_task_id", sa.String(36), nullable=True))
        batch.add_column(sa.Column("context_bundle_hash", sa.String(64), nullable=True))
        batch.add_column(sa.Column("provider_model_name", sa.String(160), nullable=True))
        batch.add_column(sa.Column("provider_model_version", sa.String(160), nullable=True))
        batch.add_column(sa.Column("raw_response", sa.Text(), nullable=True))
        batch.add_column(sa.Column("parsed_output", sa.JSON(), nullable=True))
        batch.add_column(sa.Column("parse_error", sa.Text(), nullable=True))
        batch.add_column(sa.Column("parent_run_id", sa.String(36), nullable=True))
        batch.add_column(sa.Column("input_tokens", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("output_tokens", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("cached_tokens", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("cost_currency", sa.String(12), nullable=True))
        batch.add_column(sa.Column("usage_metadata", sa.JSON(), nullable=True))
        batch.add_column(sa.Column("execution_origin", sa.String(80), nullable=True))
        batch.create_foreign_key("fk_model_run_task", "creative_tasks", ["creative_task_id"], ["id"])
        batch.create_foreign_key("fk_model_run_parent", "model_runs", ["parent_run_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("model_runs") as batch:
        batch.drop_constraint("fk_model_run_parent", type_="foreignkey")
        batch.drop_constraint("fk_model_run_task", type_="foreignkey")
        for name in (
            "execution_origin",
            "usage_metadata",
            "cost_currency",
            "cached_tokens",
            "output_tokens",
            "input_tokens",
            "parent_run_id",
            "parse_error",
            "parsed_output",
            "raw_response",
            "provider_model_version",
            "provider_model_name",
            "context_bundle_hash",
            "creative_task_id",
        ):
            batch.drop_column(name)
    with op.batch_alter_table("concept_candidates") as batch:
        batch.drop_constraint("fk_concept_batch", type_="foreignkey")
        batch.drop_column("mechanism_fingerprint")
        batch.drop_column("batch_id")
    op.drop_table("story_audit_records")
    op.drop_table("manual_evaluations")
    op.drop_table("concept_batches")
