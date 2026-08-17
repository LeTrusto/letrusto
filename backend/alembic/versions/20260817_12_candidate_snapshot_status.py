"""mark legacy candidates without captured snapshots

Revision ID: 20260817_12
Revises: 20260817_11
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260817_12"
down_revision: str | None = "20260817_11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "supplier_candidates",
        sa.Column(
            "snapshot_status",
            sa.String(length=40),
            nullable=False,
            server_default="LEGACY_SNAPSHOT_UNAVAILABLE",
        ),
    )


def downgrade() -> None:
    op.drop_column("supplier_candidates", "snapshot_status")