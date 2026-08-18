"""add Cashfree payment tracking to orders

Revision ID: 20260818_14
Revises: 20260818_13
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260818_14"
down_revision: str | None = "20260818_13"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for name, column in [
        ("payment_provider", sa.String(30)),
        ("provider_order_id", sa.String(120)),
        ("payment_session_id", sa.String(500)),
        ("payment_attempted_at", sa.DateTime(timezone=True)),
        ("paid_at", sa.DateTime(timezone=True)),
        ("payment_failure_reason", sa.String(500)),
        ("provider_reference", sa.String(160)),
    ]:
        op.add_column("orders", sa.Column(name, column, nullable=True))
    op.create_unique_constraint("uq_orders_provider_order_id", "orders", ["provider_order_id"])
    op.create_index("ix_orders_provider_order_id", "orders", ["provider_order_id"])
    op.create_table(
        "payment_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_order_id", sa.String(120), nullable=False),
        sa.Column("provider_payment_id", sa.String(160), nullable=True),
        sa.Column("session_id", sa.String(500), nullable=True),
        sa.Column("status", sa.String(30), server_default="PENDING", nullable=False),
        sa.Column("failure_reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("provider", "provider_payment_id", name="uq_payment_attempt_provider_payment"),
    )
    op.create_index("ix_payment_attempts_order_id", "payment_attempts", ["order_id"])


def downgrade() -> None:
    op.drop_table("payment_attempts")
    op.drop_index("ix_orders_provider_order_id", table_name="orders")
    op.drop_constraint("uq_orders_provider_order_id", "orders", type_="unique")
    for name in ("payment_provider", "provider_order_id", "payment_session_id", "payment_attempted_at", "paid_at", "payment_failure_reason", "provider_reference"):
        op.drop_column("orders", name)