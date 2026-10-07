"""Store the explicit model frozen for each authorized provider.

Revision ID: d8e4c1b27a55
Revises: c5a1e8d42f06
Create Date: 2026-10-06 23:15:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d8e4c1b27a55"
down_revision: str | None = "c5a1e8d42f06"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("run_authorizations") as batch:
        batch.add_column(sa.Column("provider_models", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("run_authorizations") as batch:
        batch.drop_column("provider_models")
