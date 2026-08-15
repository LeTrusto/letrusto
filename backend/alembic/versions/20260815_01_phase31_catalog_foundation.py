"""phase 3.1 catalog foundation

Revision ID: 20260815_01
Revises: 20260811_02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260815_01"
down_revision: str | None = "20260811_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("products", sa.Column("status", sa.String(length=20), nullable=True))
    op.add_column("products", sa.Column("supplier", sa.String(length=40), nullable=True))
    op.add_column("products", sa.Column("supplier_product_id", sa.String(length=120), nullable=True))
    op.add_column("products", sa.Column("supplier_source_url", sa.Text(), nullable=True))
    op.add_column("products", sa.Column("supplier_cost", sa.Numeric(12, 2), nullable=True))
    op.add_column("products", sa.Column("shipping_cost", sa.Numeric(12, 2), nullable=True))
    op.add_column("products", sa.Column("selling_price", sa.Numeric(12, 2), nullable=True))
    op.add_column("products", sa.Column("total_inventory", sa.Integer(), nullable=True))
    op.add_column("products", sa.Column("cj_inventory", sa.Integer(), nullable=True))
    op.add_column("products", sa.Column("factory_inventory", sa.Integer(), nullable=True))
    op.add_column("products", sa.Column("verified_warehouse", sa.String(length=20), nullable=True))
    op.add_column("products", sa.Column("last_supplier_sync_at", sa.DateTime(timezone=True), nullable=True))

    for column in ("category_id", "brand_id", "price_value", "rating", "ai_score", "ai_summary", "review_summary"):
        op.alter_column("products", column, nullable=True)

    op.execute("UPDATE products SET status = 'ACTIVE' WHERE status IS NULL")
    op.alter_column("products", "status", nullable=False, server_default="ACTIVE")
    op.create_index("ix_products_status", "products", ["status"])
    op.create_index("ix_products_supplier", "products", ["supplier"])
    op.create_index("ix_products_supplier_product_id", "products", ["supplier_product_id"])
    op.create_unique_constraint(
        "uq_products_supplier_product_id", "products", ["supplier", "supplier_product_id"]
    )

    op.create_table(
        "product_variants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_variant_id", sa.String(length=120), nullable=False),
        sa.Column("supplier_variant_sku", sa.String(length=160), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("attributes", sa.Text(), nullable=False),
        sa.Column("supplier_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_inventory", sa.Integer(), nullable=True),
        sa.Column("cj_inventory", sa.Integer(), nullable=True),
        sa.Column("factory_inventory", sa.Integer(), nullable=True),
        sa.Column("verified_warehouse", sa.String(length=20), nullable=True),
        sa.Column("weight_grams", sa.Numeric(12, 2), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "supplier_variant_id", name="uq_product_variants_product_supplier_id"),
    )
    op.create_index("ix_product_variants_product_id", "product_variants", ["product_id"])
    op.create_index("ix_product_variants_supplier_variant_id", "product_variants", ["supplier_variant_id"])


def downgrade() -> None:
    op.drop_index("ix_product_variants_supplier_variant_id", table_name="product_variants")
    op.drop_index("ix_product_variants_product_id", table_name="product_variants")
    op.drop_table("product_variants")
    op.drop_constraint("uq_products_supplier_product_id", "products", type_="unique")
    op.drop_index("ix_products_supplier_product_id", table_name="products")
    op.drop_index("ix_products_supplier", table_name="products")
    op.drop_index("ix_products_status", table_name="products")
    for column in ("category_id", "brand_id", "price_value", "rating", "ai_score", "ai_summary", "review_summary"):
        op.alter_column("products", column, nullable=False)
    op.drop_column("products", "last_supplier_sync_at")
    op.drop_column("products", "verified_warehouse")
    op.drop_column("products", "factory_inventory")
    op.drop_column("products", "cj_inventory")
    op.drop_column("products", "total_inventory")
    op.drop_column("products", "selling_price")
    op.drop_column("products", "shipping_cost")
    op.drop_column("products", "supplier_cost")
    op.drop_column("products", "supplier_source_url")
    op.drop_column("products", "supplier_product_id")
    op.drop_column("products", "supplier")
    op.drop_column("products", "status")