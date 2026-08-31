"""configure the initial LeTrusto India shipping estimate

Revision ID: 20260831_33
Revises: 20260831_32
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260831_33"
down_revision: str | None = "20260831_32"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "printful_shipping_rates",
        sa.Column("rate_source", sa.String(length=40), nullable=False, server_default="PRINTFUL_PUBLISHED"),
    )
    op.execute(
        sa.text(
            """
            UPDATE printful_shipping_rates
            SET currency = 'INR',
                single_product_rate = 299.00,
                additional_product_rate = 100.00,
                rate_source = 'LETRUSTO_ESTIMATE',
                requires_verification = TRUE,
                country_codes = '[]'::json
            WHERE category_key = 'hoodies-sweatshirts'
              AND destination_region = 'IN'
              AND source = 'printful'
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE printful_shipping_rates
            SET currency = 'USD',
                single_product_rate = NULL,
                additional_product_rate = NULL,
                rate_source = 'PRINTFUL_PUBLISHED',
                requires_verification = TRUE
            WHERE category_key = 'hoodies-sweatshirts'
              AND destination_region = 'IN'
              AND source = 'printful'
            """
        )
    )
    op.drop_column("printful_shipping_rates", "rate_source")
