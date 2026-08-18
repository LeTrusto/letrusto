"""add refund_requests table for cancellation/refund lifecycle

Revision ID: 20260818_17
Revises: 20260818_16
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "20260818_17"
down_revision: str | None = "20260818_16"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "refund_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("payment_attempt_id", UUID(as_uuid=True), sa.ForeignKey("payment_attempts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_refund_id", sa.String(200), nullable=True),
        sa.Column("provider_order_id", sa.String(120), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(8), nullable=False, server_default="INR"),
        sa.Column("status", sa.String(30), nullable=False, server_default="PENDING"),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("idempotency_key", sa.String(200), nullable=False),
        sa.Column("requested_by", sa.String(80), nullable=False, server_default="customer"),
        sa.Column("admin_id", UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("idempotency_key", name="uq_refund_requests_idempotency_key"),
    )
    op.create_index("ix_refund_requests_provider_refund_id", "refund_requests", ["provider_refund_id"], unique=False)

    op.add_column("orders", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("cancellation_reason", sa.String(500), nullable=True))
    op.add_column("orders", sa.Column("cancelled_by", sa.String(80), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "cancelled_by")
    op.drop_column("orders", "cancellation_reason")
    op.drop_column("orders", "cancelled_at")
    op.drop_index("ix_refund_requests_provider_refund_id", table_name="refund_requests")
    op.drop_table("refund_requests")
