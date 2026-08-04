"""affiliate link fields on products

Revision ID: 20260804_01
Revises: 20260803_04
Create Date: 2026-08-04
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260804_01"
down_revision: str | None = "20260803_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("products", sa.Column("amazon_asin", sa.String(length=20), nullable=True))
    op.add_column("products", sa.Column("amazon_affiliate_url", sa.Text(), nullable=True))
    op.add_column("products", sa.Column("flipkart_affiliate_url", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "flipkart_affiliate_url")
    op.drop_column("products", "amazon_affiliate_url")
    op.drop_column("products", "amazon_asin")
