"""store verified Printful supplier shipping provenance

Revision ID: 20260901_38
Revises: 20260901_37
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260901_38"
down_revision: str | None = "20260901_37"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    columns = (
        ("supplier_single_product_rate", sa.Numeric(12, 2)),
        ("supplier_additional_product_rate", sa.Numeric(12, 2)),
        ("supplier_currency", sa.String(8)),
        ("supplier_to_customer_fx_rate", sa.Numeric(12, 4)),
    )
    for name, column_type in columns:
        op.add_column("printful_shipping_rates", sa.Column(name, column_type, nullable=True))


def downgrade() -> None:
    for name in (
        "supplier_to_customer_fx_rate",
        "supplier_currency",
        "supplier_additional_product_rate",
        "supplier_single_product_rate",
    ):
        op.drop_column("printful_shipping_rates", name)
