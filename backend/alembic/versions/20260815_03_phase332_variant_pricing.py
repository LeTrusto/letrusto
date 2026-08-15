"""phase 3.3.2 variant pricing

Revision ID: 20260815_03
Revises: 20260815_02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260815_03"
down_revision: str | None = "20260815_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "product_variants",
        sa.Column("selling_price", sa.Numeric(12, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("product_variants", "selling_price")