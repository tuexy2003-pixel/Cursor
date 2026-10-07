"""Safe execution: run authorizations, invocations, and fingerprint provenance.

Revision ID: c5a1e8d42f06
Revises: b3d8f1a64c20
Create Date: 2026-10-06 22:20:00
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c5a1e8d42f06"
down_revision: str | None = "b3d8f1a64c20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "run_authorizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("context_bundle_id", sa.String(36), sa.ForeignKey("context_bundles.id"), nullable=False),
        sa.Column("context_bundle_hash", sa.String(64), nullable=False),
        sa.Column("provider_name", sa.String(80), nullable=False),
        sa.Column("model_name", sa.String(160), nullable=False),
        sa.Column("stage", sa.String(80), nullable=False),
        sa.Column("created_by", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("attempts_used", sa.Integer(), nullable=False),
        sa.Column("max_output_tokens", sa.Integer(), nullable=True),
        sa.Column("max_input_tokens", sa.Integer(), nullable=True),
        sa.Column("max_providers", sa.Integer(), nullable=False),
        sa.Column("allowed_providers", sa.JSON(), nullable=False),
        sa.Column("max_cost", sa.Numeric(12, 4), nullable=True),
        sa.Column("currency", sa.String(12), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(160), nullable=True),
        sa.UniqueConstraint("idempotency_key", name="uq_run_authorization_key"),
    )
    op.create_table(
        "provider_invocations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("idempotency_key", sa.String(160), nullable=False),
        sa.Column("authorization_id", sa.String(36), sa.ForeignKey("run_authorizations.id"), nullable=False),
        sa.Column("provider_name", sa.String(80), nullable=False),
        sa.Column("model_name", sa.String(160), nullable=False),
        sa.Column("context_bundle_id", sa.String(36), sa.ForeignKey("context_bundles.id"), nullable=False),
        sa.Column("context_bundle_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("model_run_id", sa.String(36), sa.ForeignKey("model_runs.id"), nullable=True),
        sa.Column("provider_request_id", sa.String(160), nullable=True),
        sa.Column("network_attempts", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.UniqueConstraint("idempotency_key", name="uq_provider_invocation_key"),
    )
    with op.batch_alter_table("model_runs") as batch:
        batch.add_column(sa.Column("run_authorization_id", sa.String(36), nullable=True))
        batch.add_column(sa.Column("provider_request_id", sa.String(160), nullable=True))
        batch.add_column(sa.Column("execution_state", sa.String(40), nullable=True))
        batch.create_foreign_key(
            "fk_model_run_authorization",
            "run_authorizations",
            ["run_authorization_id"],
            ["id"],
        )
    _relabel_deterministic_fingerprints()


def downgrade() -> None:
    with op.batch_alter_table("model_runs") as batch:
        batch.drop_constraint("fk_model_run_authorization", type_="foreignkey")
        batch.drop_column("execution_state")
        batch.drop_column("provider_request_id")
        batch.drop_column("run_authorization_id")
    op.drop_table("provider_invocations")
    op.drop_table("run_authorizations")


def _relabel_deterministic_fingerprints() -> None:
    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, mechanism_fingerprint FROM concept_candidates")).fetchall()
    for row in rows:
        data = _load_json(row.mechanism_fingerprint)
        if not isinstance(data, dict):
            continue
        changed = False
        for value in data.values():
            if not isinstance(value, dict):
                continue
            if value.get("assignment") != "model_extracted":
                continue
            if value.get("source") != "deterministic skeleton phrases":
                continue
            value["assignment"] = "DETERMINISTIC_INFERRED"
            changed = True
        if changed:
            connection.execute(
                sa.text("UPDATE concept_candidates SET mechanism_fingerprint = :payload WHERE id = :id"),
                {"payload": json.dumps(data), "id": row.id},
            )


def _load_json(value: object) -> object:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None
    return value
