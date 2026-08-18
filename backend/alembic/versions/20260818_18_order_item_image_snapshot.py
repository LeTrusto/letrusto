"""add historical order item image snapshot

Revision ID: 20260818_18
Revises: 20260818_17
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260818_18"
down_revision: str | None = "20260818_17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("order_items", sa.Column("product_image_url", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("order_items", "product_image_url")