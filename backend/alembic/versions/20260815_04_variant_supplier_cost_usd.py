"""store exact variant supplier cost in source currency

Revision ID: 20260815_04
Revises: 20260815_03
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260815_04"
down_revision: str | None = "20260815_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "product_variants",
        sa.Column("supplier_cost_usd", sa.Numeric(12, 4), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("product_variants", "supplier_cost_usd")