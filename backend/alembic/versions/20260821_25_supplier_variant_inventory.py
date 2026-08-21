"""add warehouse-level supplier variant inventory

Revision ID: 20260821_25
Revises: 20260819_24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = "20260821_25"
down_revision: str | None = "20260819_24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "supplier_variant_inventory",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("product_id", UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("variant_id", UUID(as_uuid=True), sa.ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("supplier", sa.String(40), nullable=False, server_default="cj"),
        sa.Column("supplier_product_id", sa.String(120), nullable=False),
        sa.Column("supplier_variant_id", sa.String(120), nullable=False),
        sa.Column("warehouse_identity", sa.String(180), nullable=False),
        sa.Column("warehouse_country", sa.String(20), nullable=False),
        sa.Column("storage_id", sa.String(120), nullable=True),
        sa.Column("warehouse_name", sa.String(200), nullable=True),
        sa.Column("total_inventory", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cj_sellable_inventory", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("factory_inventory", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("verification_status", sa.String(30), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint(
            "supplier",
            "supplier_variant_id",
            "warehouse_identity",
            name="uq_supplier_variant_inventory_identity",
        ),
    )
    op.create_index(
        "ix_supplier_variant_inventory_variant_country",
        "supplier_variant_inventory",
        ["variant_id", "warehouse_country"],
    )
    op.create_index(
        "ix_supplier_variant_inventory_product_variant",
        "supplier_variant_inventory",
        ["product_id", "supplier_variant_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_supplier_variant_inventory_product_variant", table_name="supplier_variant_inventory")
    op.drop_index("ix_supplier_variant_inventory_variant_country", table_name="supplier_variant_inventory")
    op.drop_table("supplier_variant_inventory")