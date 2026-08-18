"""add supplier fulfillment tracking to orders

Revision ID: 20260818_15
Revises: 20260818_14
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260818_15"
down_revision: str | None = "20260818_14"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for name, column in [
        ("supplier_order_id", sa.String(160)),
        ("fulfillment_submitted_at", sa.DateTime(timezone=True)),
        ("fulfillment_failure_reason", sa.String(500)),
        ("tracking_number", sa.String(160)),
        ("tracking_carrier", sa.String(120)),
        ("shipped_at", sa.DateTime(timezone=True)),
        ("delivered_at", sa.DateTime(timezone=True)),
    ]:
        op.add_column("orders", sa.Column(name, column, nullable=True))
    op.create_unique_constraint("uq_orders_supplier_order_id", "orders", ["supplier_order_id"])
    op.create_index("ix_orders_supplier_order_id", "orders", ["supplier_order_id"])


def downgrade() -> None:
    op.drop_index("ix_orders_supplier_order_id", table_name="orders")
    op.drop_constraint("uq_orders_supplier_order_id", "orders", type_="unique")
    for name in ("supplier_order_id", "fulfillment_submitted_at", "fulfillment_failure_reason", "tracking_number", "tracking_carrier", "shipped_at", "delivered_at"):
        op.drop_column("orders", name)