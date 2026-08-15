"""add commercial product review state

Revision ID: 20260815_05
Revises: 20260815_04
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260815_05"
down_revision: str | None = "20260815_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("commercial_status", sa.String(length=20), server_default="DRAFT", nullable=False),
    )
    op.add_column(
        "products",
        sa.Column("commercial_reasons", sa.JSON(), server_default="[]", nullable=False),
    )
    op.add_column(
        "products",
        sa.Column("commercial_reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "products",
        sa.Column("supplier_validation_status", sa.String(length=20), nullable=True),
    )
    op.create_index("ix_products_commercial_status", "products", ["commercial_status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_products_commercial_status", table_name="products")
    op.drop_column("products", "supplier_validation_status")
    op.drop_column("products", "commercial_reviewed_at")
    op.drop_column("products", "commercial_reasons")
    op.drop_column("products", "commercial_status")