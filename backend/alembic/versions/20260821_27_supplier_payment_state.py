"""add supplier payment state and timestamps

Revision ID: 20260821_27
Revises: 20260821_26
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260821_27"
down_revision: str | None = "20260821_26"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for name, column in [
        ("supplier_payment_state", sa.String(20)),
        ("supplier_payment_attempted_at", sa.DateTime(timezone=True)),
        ("supplier_payment_confirmed_at", sa.DateTime(timezone=True)),
        ("supplier_payment_error", sa.String(500)),
        ("supplier_payment_updated_at", sa.DateTime(timezone=True)),
    ]:
        op.add_column("orders", sa.Column(name, column, nullable=True))


def downgrade() -> None:
    for name in (
        "supplier_payment_updated_at",
        "supplier_payment_error",
        "supplier_payment_confirmed_at",
        "supplier_payment_attempted_at",
        "supplier_payment_state",
    ):
        op.drop_column("orders", name)