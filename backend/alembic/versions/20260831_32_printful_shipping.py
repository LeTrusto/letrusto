"""add configurable Printful shipping reference rates

Revision ID: 20260831_32
Revises: 20260828_31
"""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4
from alembic import op
import sqlalchemy as sa

revision: str = "20260831_32"
down_revision: str | None = "20260828_31"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "printful_shipping_rates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=True),
        sa.Column("source", sa.String(length=40), nullable=False, server_default="printful"),
        sa.Column("category_key", sa.String(length=80), nullable=False, server_default="hoodies-sweatshirts"),
        sa.Column("destination_region", sa.String(length=40), nullable=False),
        sa.Column("country_codes", sa.JSON(), nullable=False),
        sa.Column("shipping_method", sa.String(length=120), nullable=False, server_default="Standard"),
        sa.Column("single_product_rate", sa.Numeric(12, 2), nullable=True),
        sa.Column("additional_product_rate", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="USD"),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("requires_verification", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "category_key", "destination_region", name="uq_printful_shipping_rate_scope"),
    )
    op.create_index("ix_printful_shipping_rates_product_id", "printful_shipping_rates", ["product_id"])
    op.create_index("ix_printful_shipping_rates_destination", "printful_shipping_rates", ["destination_region"])

    now = datetime.now(timezone.utc)
    rates = {
        "IN": ([], None, None, True), "US": (["US"], "8.79", "2.50", False), "GB": (["GB"], "7.29", "2.40", False),
        "EU": (["AT", "BE", "BG", "HR", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"], "7.29", "2.40", False),
        "CA": (["CA"], "10.59", "2.35", False), "AU_NZ": (["AU", "NZ"], "12.49", "2.25", False), "JP": (["JP"], "7.89", "2.60", False),
        "BR": (["BR"], "17.69", "8.00", False), "WORLDWIDE": (["CH", "NO", "IS", "LI", "SG", "MY", "MX", "ZA", "AE", "HK", "TW", "KR"], "17.69", "8.00", False),
    }
    table = sa.table("printful_shipping_rates", sa.column("id", sa.UUID()), sa.column("source", sa.String()), sa.column("category_key", sa.String()), sa.column("destination_region", sa.String()), sa.column("country_codes", sa.JSON()), sa.column("shipping_method", sa.String()), sa.column("single_product_rate", sa.Numeric()), sa.column("additional_product_rate", sa.Numeric()), sa.column("currency", sa.String()), sa.column("effective_at", sa.DateTime(timezone=True)), sa.column("active", sa.Boolean()), sa.column("requires_verification", sa.Boolean()))
    op.bulk_insert(table, [{"id": uuid4(), "source": "printful", "category_key": "hoodies-sweatshirts", "destination_region": region, "country_codes": countries, "shipping_method": "Standard", "single_product_rate": single, "additional_product_rate": additional, "currency": "USD", "effective_at": now, "active": True, "requires_verification": verify} for region, (countries, single, additional, verify) in rates.items()])


def downgrade() -> None:
    op.drop_index("ix_printful_shipping_rates_destination", table_name="printful_shipping_rates")
    op.drop_index("ix_printful_shipping_rates_product_id", table_name="printful_shipping_rates")
    op.drop_table("printful_shipping_rates")
