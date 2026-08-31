"""update current Printful hoodie launch rates and retail prices

Revision ID: 20260831_34
Revises: 20260831_33
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260831_34"
down_revision: str | None = "20260831_33"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    rates = {
        "US": ("8.49", "2.50"),
        "EU": ("6.99", "2.40"),
        "GB": ("6.99", "2.40"),
        "CA": ("10.19", "2.35"),
        "AU_NZ": ("11.99", "2.25"),
        "JP": ("7.59", "2.60"),
        "BR": ("16.99", "8.00"),
        "WORLDWIDE": ("16.99", "8.00"),
    }
    for region, (single, additional) in rates.items():
        op.execute(
            sa.text(
                """
                UPDATE printful_shipping_rates
                SET single_product_rate = CAST(:single AS numeric),
                    additional_product_rate = CAST(:additional AS numeric),
                    currency = 'USD',
                    rate_source = 'PRINTFUL_PUBLISHED',
                    updated_at = now()
                WHERE category_key = 'hoodies-sweatshirts'
                  AND destination_region = :region
                  AND source = 'printful'
                """
            ).bindparams(single=single, additional=additional, region=region)
        )

    op.execute(
        sa.text(
            """
            UPDATE products
            SET price_value = 4499.00,
                selling_price = 4499.00,
                currency = 'INR',
                supplier_validation_details = (
                    COALESCE(supplier_validation_details::jsonb, '{}'::jsonb)
                    || jsonb_build_object(
                        'printful_customer_pricing',
                        jsonb_build_object(
                            'india_price_inr', '4499.00',
                            'international_price_usd', '59.99',
                            'shipping_reviewed', TRUE
                        )
                    )
                )::json
            WHERE supplier = 'printful'
              AND status = 'DRAFT'
              AND lower(name) LIKE '%hoodie%'
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE product_variants
            SET selling_price = 4499.00
            WHERE active = TRUE
              AND product_id IN (
                  SELECT id FROM products
                  WHERE supplier = 'printful'
                    AND status = 'DRAFT'
                    AND lower(name) LIKE '%hoodie%'
              )
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE products
            SET supplier_product_id = '462173612'
            WHERE id = (
                SELECT id FROM products
                WHERE supplier = 'printful'
                  AND status = 'DRAFT'
                  AND lower(name) LIKE '%hoodie%'
                  AND supplier_validation_details->>'source' = 'PRINTFUL_SYNC_PRODUCT_IMPORT'
                ORDER BY created_at ASC
                LIMIT 1
            )
            """
        )
    )


def downgrade() -> None:
    raise RuntimeError("20260831_34 is a launch data update and must be reverted with an approved data migration")
