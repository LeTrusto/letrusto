"""add product market price evidence

Revision ID: 20260815_07
Revises: 20260815_06
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260815_07"
down_revision: str | None = "20260815_06"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "product_market_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("competitor_name", sa.String(length=160), nullable=False),
        sa.Column("product_name", sa.String(length=240), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("observed_price_inr", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), server_default="INR", nullable=False),
        sa.Column("variant_description", sa.String(length=240), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("currency = 'INR'", name="ck_product_market_evidence_currency_inr"),
        sa.CheckConstraint("observed_price_inr > 0", name="ck_product_market_evidence_positive_price"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_product_market_evidence_product_id", "product_market_evidence", ["product_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_product_market_evidence_product_id", table_name="product_market_evidence")
    op.drop_table("product_market_evidence")