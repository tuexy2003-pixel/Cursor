"""preservation baseline columns

Revision ID: b7c1a9e0d4f2
Revises: 76f00d0e35cb
Create Date: 2026-10-06 17:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b7c1a9e0d4f2"
down_revision: str | None = "76f00d0e35cb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("size_bytes", sa.Integer(), nullable=True))
    with op.batch_alter_table("skill_artifacts") as batch_op:
        batch_op.add_column(sa.Column("current_version_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            "fk_skill_current_version",
            "skill_versions",
            ["current_version_id"],
            ["id"],
        )
    op.create_table(
        "example_links",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("benchmark_id", sa.String(length=36), nullable=True),
        sa.Column("regression_test_id", sa.String(length=36), nullable=True),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("example_role", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["benchmark_id"], ["benchmark_creatives.id"]),
        sa.ForeignKeyConstraint(["regression_test_id"], ["regression_tests.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("benchmark_id", "regression_test_id", "asset_id", "example_role"),
    )


def downgrade() -> None:
    op.drop_table("example_links")
    with op.batch_alter_table("skill_artifacts") as batch_op:
        batch_op.drop_constraint("fk_skill_current_version", type_="foreignkey")
        batch_op.drop_column("current_version_id")
    op.drop_column("assets", "size_bytes")
