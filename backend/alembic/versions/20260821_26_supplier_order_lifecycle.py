"""add supplier order lifecycle payment metadata

Revision ID: 20260821_26
Revises: 20260821_25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260821_26"
down_revision: str | None = "20260821_25"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for name, column in [
        ("supplier_pay_id", sa.String(200)),
        ("supplier_payment_url", sa.Text()),
        ("supplier_shipment_order_id", sa.String(200)),
        ("supplier_origin", sa.String(40)),
        ("supplier_logistic_name", sa.String(160)),
        ("supplier_status_updated_at", sa.DateTime(timezone=True)),
    ]:
        op.add_column("orders", sa.Column(name, column, nullable=True))


def downgrade() -> None:
    for name in (
        "supplier_status_updated_at",
        "supplier_logistic_name",
        "supplier_origin",
        "supplier_shipment_order_id",
        "supplier_payment_url",
        "supplier_pay_id",
    ):
        op.drop_column("orders", name)