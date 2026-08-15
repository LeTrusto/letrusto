"""remove obsolete legacy affiliate catalog

Revision ID: 20260815_02
Revises: 20260815_01
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260815_02"
down_revision: str | None = "20260815_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Product-specific foreign keys use CASCADE or SET NULL. Supplier-backed
    # products are protected by the supplier discriminator.
    op.execute("DELETE FROM products WHERE supplier IS NULL")


def downgrade() -> None:
    raise RuntimeError("Legacy affiliate catalog data cannot be restored")