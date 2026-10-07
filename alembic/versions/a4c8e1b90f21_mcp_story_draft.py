"""MCP audit fields and StoryLock draft provenance.

Revision ID: a4c8e1b90f21
Revises: e7b2a9c14d30
Create Date: 2026-10-07 16:30:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a4c8e1b90f21"
down_revision: str | None = "e7b2a9c14d30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("mcp_audit_logs") as batch:
        batch.add_column(sa.Column("request_id", sa.String(length=80), nullable=True))
        batch.add_column(sa.Column("input_hash", sa.String(length=64), nullable=True))
    with op.batch_alter_table("story_lock_versions") as batch:
        batch.add_column(sa.Column("provenance", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("story_lock_versions") as batch:
        batch.drop_column("provenance")
    with op.batch_alter_table("mcp_audit_logs") as batch:
        batch.drop_column("input_hash")
        batch.drop_column("request_id")
