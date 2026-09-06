"""add SaaS trial, entitlement lifecycle, webhook ledger, and widget usage

Revision ID: 20260906_43
Revises: 20260905_42
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260906_43"
down_revision: str | None = "20260905_42"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("subscriptions", sa.Column("failure_reason", sa.String(length=500), nullable=True))
    op.add_column("subscriptions", sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("subscriptions", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("subscriptions", sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("subscriptions", sa.Column("grace_until", sa.DateTime(timezone=True), nullable=True))
    op.create_table(
        "subscription_webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_event_id", sa.String(length=200), nullable=False),
        sa.Column("event_name", sa.String(length=100), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_event_id"),
    )
    op.create_table(
        "widget_usage",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("widget_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["widget_id"], ["widgets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("widget_id", "period_start", name="uq_widget_usage_period"),
    )
    op.create_index("ix_widget_usage_widget_id", "widget_usage", ["widget_id"])


def downgrade() -> None:
    op.drop_index("ix_widget_usage_widget_id", table_name="widget_usage")
    op.drop_table("widget_usage")
    op.drop_table("subscription_webhook_events")
    for column in ("grace_until", "cancel_at_period_end", "cancelled_at", "failed_at", "failure_reason"):
        op.drop_column("subscriptions", column)
    op.drop_column("users", "trial_ends_at")
    op.drop_column("users", "trial_started_at")