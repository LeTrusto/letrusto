"""add inventory reservations for checkout protection

Revision ID: 20260818_19
Revises: 20260818_18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "20260818_19"
down_revision: str | None = "20260818_18"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inventory_reservations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_item_id", UUID(as_uuid=True), sa.ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("variant_id", UUID(as_uuid=True), sa.ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.CheckConstraint("quantity > 0", name="ck_inventory_reservations_positive_quantity"),
        sa.CheckConstraint("status IN ('ACTIVE', 'RELEASED', 'CONSUMED', 'EXPIRED')", name="ck_inventory_reservations_status"),
        sa.UniqueConstraint("order_item_id", name="uq_inventory_reservations_order_item"),
    )
    op.create_index("ix_inventory_reservations_variant_status", "inventory_reservations", ["variant_id", "status"])
    op.create_index("ix_inventory_reservations_order_status", "inventory_reservations", ["order_id", "status"])
    op.create_index("ix_inventory_reservations_expires_status", "inventory_reservations", ["expires_at", "status"])


def downgrade() -> None:
    op.drop_index("ix_inventory_reservations_expires_status", table_name="inventory_reservations")
    op.drop_index("ix_inventory_reservations_order_status", table_name="inventory_reservations")
    op.drop_index("ix_inventory_reservations_variant_status", table_name="inventory_reservations")
    op.drop_table("inventory_reservations")
