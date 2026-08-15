"""add approved supplier candidate staging

Revision ID: 20260815_09
Revises: 20260815_08
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260815_09"
down_revision: str | None = "20260815_08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "supplier_candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier", sa.String(length=40), nullable=False),
        sa.Column("supplier_product_id", sa.String(length=120), nullable=False),
        sa.Column("supplier_sku", sa.String(length=160), nullable=True),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("approval_status", sa.String(length=20), nullable=False),
        sa.Column("supplier_validation_status", sa.String(length=20), nullable=True),
        sa.Column("supplier_validation_score", sa.Integer(), nullable=True),
        sa.Column("commercial_status", sa.String(length=20), nullable=False),
        sa.Column("market_status", sa.String(length=30), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("imported_product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["approved_by_user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["imported_product_id"], ["products.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "supplier",
            "supplier_product_id",
            name="uq_supplier_candidates_supplier_product_id",
        ),
    )
    op.create_index("ix_supplier_candidates_supplier", "supplier_candidates", ["supplier"])
    op.create_index(
        "ix_supplier_candidates_supplier_product_id",
        "supplier_candidates",
        ["supplier_product_id"],
    )
    op.create_index("ix_supplier_candidates_supplier_sku", "supplier_candidates", ["supplier_sku"])
    op.create_index(
        "ix_supplier_candidates_approval_status",
        "supplier_candidates",
        ["approval_status"],
    )
    op.create_index(
        "ix_supplier_candidates_approved_by_user_id",
        "supplier_candidates",
        ["approved_by_user_id"],
    )
    op.create_index(
        "ix_supplier_candidates_imported_product_id",
        "supplier_candidates",
        ["imported_product_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_supplier_candidates_imported_product_id", table_name="supplier_candidates")
    op.drop_index("ix_supplier_candidates_approved_by_user_id", table_name="supplier_candidates")
    op.drop_index("ix_supplier_candidates_approval_status", table_name="supplier_candidates")
    op.drop_index("ix_supplier_candidates_supplier_sku", table_name="supplier_candidates")
    op.drop_index("ix_supplier_candidates_supplier_product_id", table_name="supplier_candidates")
    op.drop_index("ix_supplier_candidates_supplier", table_name="supplier_candidates")
    op.drop_table("supplier_candidates")