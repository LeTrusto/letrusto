"""add order shipment notification state

Revision ID: 20260901_36
Revises: 20260831_35
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260901_36"
down_revision: str | None = "20260831_35"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("tracking_url", sa.String(length=1000), nullable=True))
    op.add_column("orders", sa.Column("shipped_email_sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("delivered_email_sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("notification_failure_reason", sa.String(length=500), nullable=True))
    op.add_column("orders", sa.Column("notification_failed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "notification_failed_at")
    op.drop_column("orders", "notification_failure_reason")
    op.drop_column("orders", "delivered_email_sent_at")
    op.drop_column("orders", "shipped_email_sent_at")
    op.drop_column("orders", "tracking_url")
