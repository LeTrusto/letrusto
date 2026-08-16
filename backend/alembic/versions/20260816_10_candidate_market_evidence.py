"""allow supplier candidates to own market evidence

Revision ID: 20260816_10
Revises: 20260815_09
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260816_10"
down_revision: str | None = "20260815_09"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "supplier_candidates",
        sa.Column("discovery_min_selling_price_inr", sa.Numeric(12, 2), nullable=True),
    )
    op.add_column(
        "supplier_candidates",
        sa.Column("discovery_max_selling_price_inr", sa.Numeric(12, 2), nullable=True),
    )
    op.alter_column("product_market_evidence", "product_id", nullable=True)
    op.add_column(
        "product_market_evidence",
        sa.Column("supplier_candidate_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_product_market_evidence_supplier_candidate_id",
        "product_market_evidence",
        "supplier_candidates",
        ["supplier_candidate_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_product_market_evidence_supplier_candidate_id",
        "product_market_evidence",
        ["supplier_candidate_id"],
    )
    op.create_check_constraint(
        "ck_product_market_evidence_exactly_one_owner",
        "product_market_evidence",
        "(product_id IS NOT NULL) <> (supplier_candidate_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_product_market_evidence_exactly_one_owner",
        "product_market_evidence",
        type_="check",
    )
    op.drop_index(
        "ix_product_market_evidence_supplier_candidate_id",
        table_name="product_market_evidence",
    )
    op.drop_constraint(
        "fk_product_market_evidence_supplier_candidate_id",
        "product_market_evidence",
        type_="foreignkey",
    )
    op.drop_column("product_market_evidence", "supplier_candidate_id")
    op.alter_column("product_market_evidence", "product_id", nullable=False)
    op.drop_column("supplier_candidates", "discovery_max_selling_price_inr")
    op.drop_column("supplier_candidates", "discovery_min_selling_price_inr")