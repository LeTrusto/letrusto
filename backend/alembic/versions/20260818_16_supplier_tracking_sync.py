"""add supplier tracking sync metadata

Revision ID: 20260818_16
Revises: 20260818_15
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260818_16"
down_revision: str | None = "20260818_15"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("supplier_status", sa.String(80), nullable=True))
    op.add_column("orders", sa.Column("last_supplier_sync_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "last_supplier_sync_at")
    op.drop_column("orders", "supplier_status")