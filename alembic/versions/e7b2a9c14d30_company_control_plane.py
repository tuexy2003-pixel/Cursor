"""Company control plane tables.

Revision ID: e7b2a9c14d30
Revises: d8e4c1b27a55
Create Date: 2026-10-07 15:30:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e7b2a9c14d30"
down_revision: str | None = "d8e4c1b27a55"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "work_orders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("program_id", sa.String(length=36), nullable=False),
        sa.Column("account_id", sa.String(length=36), nullable=True),
        sa.Column("campaign_id", sa.String(length=36), nullable=True),
        sa.Column("creative_id", sa.String(length=36), nullable=True),
        sa.Column("priority", sa.String(length=40), nullable=False),
        sa.Column("requested_by", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("task_ids", sa.JSON(), nullable=False),
        sa.Column("reference_requirements", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.ForeignKeyConstraint(["creative_id"], ["creatives.id"]),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_work_orders_status", "work_orders", ["status", "created_at"])
    op.create_table(
        "workflow_definitions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("key", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_table(
        "workflow_definition_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("definition_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("graph", sa.JSON(), nullable=False),
        sa.Column("graph_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["definition_id"], ["workflow_definitions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("definition_id", "version_number"),
    )
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("work_order_id", sa.String(length=36), nullable=False),
        sa.Column("definition_version_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("memory", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["definition_version_id"], ["workflow_definition_versions.id"]),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "step_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workflow_run_id", sa.String(length=36), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("node_id", sa.String(length=80), nullable=False),
        sa.Column("node_kind", sa.String(length=80), nullable=False),
        sa.Column("input_refs", sa.JSON(), nullable=False),
        sa.Column("output_refs", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("specialist_role", sa.String(length=80), nullable=True),
        sa.Column("capability", sa.String(length=80), nullable=True),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column("evidence_ids", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workflow_run_id", "node_id"),
    )
    op.create_table(
        "workflow_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workflow_run_id", sa.String(length=36), nullable=False),
        sa.Column("step_run_id", sa.String(length=36), nullable=True),
        sa.Column("from_status", sa.String(length=40), nullable=True),
        sa.Column("to_status", sa.String(length=40), nullable=False),
        sa.Column("actor", sa.String(length=160), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["step_run_id"], ["step_runs.id"]),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "specialists",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=80), nullable=False),
        sa.Column("capabilities", sa.JSON(), nullable=False),
        sa.Column("transports", sa.JSON(), nullable=False),
        sa.Column("authoritative", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role"),
    )
    op.create_table(
        "specialist_assignments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("step_run_id", sa.String(length=36), nullable=False),
        sa.Column("specialist_role", sa.String(length=80), nullable=False),
        sa.Column("transport", sa.String(length=40), nullable=False),
        sa.Column("creative_task_id", sa.String(length=36), nullable=True),
        sa.Column("context_bundle_id", sa.String(length=36), nullable=True),
        sa.Column("context_bundle_hash", sa.String(length=64), nullable=True),
        sa.Column("provider_name", sa.String(length=80), nullable=True),
        sa.Column("model_name", sa.String(length=160), nullable=True),
        sa.Column("api_verified", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("contract_name", sa.String(length=80), nullable=False),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("parsed_response", sa.JSON(), nullable=True),
        sa.Column("validation_status", sa.String(length=40), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_refs", sa.JSON(), nullable=False),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["context_bundle_id"], ["context_bundles.id"]),
        sa.ForeignKeyConstraint(["creative_task_id"], ["creative_tasks.id"]),
        sa.ForeignKeyConstraint(["step_run_id"], ["step_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "evidence_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("evidence_type", sa.String(length=80), nullable=False),
        sa.Column("source", sa.String(length=160), nullable=False),
        sa.Column("subject_type", sa.String(length=80), nullable=False),
        sa.Column("subject_id", sa.String(length=36), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("claims_supported", sa.JSON(), nullable=False),
        sa.Column("verification_state", sa.String(length=40), nullable=False),
        sa.Column("workflow_run_id", sa.String(length=36), nullable=True),
        sa.Column("step_run_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["step_run_id"], ["step_runs.id"]),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "approval_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("approval_type", sa.String(length=80), nullable=False),
        sa.Column("subject_type", sa.String(length=80), nullable=False),
        sa.Column("subject_id", sa.String(length=36), nullable=False),
        sa.Column("subject_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("requested_by", sa.String(length=160), nullable=False),
        sa.Column("decided_by", sa.String(length=160), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("workflow_run_id", sa.String(length=36), nullable=True),
        sa.Column("step_run_id", sa.String(length=36), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["step_run_id"], ["step_runs.id"]),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "action_authorizations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("action_type", sa.String(length=80), nullable=False),
        sa.Column("subject_type", sa.String(length=80), nullable=False),
        sa.Column("subject_id", sa.String(length=64), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("target", sa.String(length=240), nullable=True),
        sa.Column("limits", sa.JSON(), nullable=False),
        sa.Column("requested_by", sa.String(length=160), nullable=False),
        sa.Column("authorizer", sa.String(length=160), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "external_executions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("action_authorization_id", sa.String(length=36), nullable=True),
        sa.Column("action_type", sa.String(length=80), nullable=False),
        sa.Column("adapter", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("detail", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["action_authorization_id"], ["action_authorizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "verification_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("external_execution_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["external_execution_id"], ["external_executions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mcp_audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("caller", sa.String(length=160), nullable=False),
        sa.Column("interface", sa.String(length=40), nullable=False),
        sa.Column("operation", sa.String(length=120), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("affected_records", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("mcp_audit_logs")
    op.drop_table("verification_results")
    op.drop_table("external_executions")
    op.drop_table("action_authorizations")
    op.drop_table("approval_requests")
    op.drop_table("evidence_records")
    op.drop_table("specialist_assignments")
    op.drop_table("specialists")
    op.drop_table("workflow_events")
    op.drop_table("step_runs")
    op.drop_table("workflow_runs")
    op.drop_table("workflow_definition_versions")
    op.drop_table("workflow_definitions")
    op.drop_index("ix_work_orders_status", table_name="work_orders")
    op.drop_table("work_orders")
