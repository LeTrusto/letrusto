"""add B2B social proof widget tables

Revision ID: 20260905_41
Revises: 20260903_40
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260905_41"
down_revision: str | None = "20260903_40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "widgets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("domain_name", sa.String(length=255), nullable=False),
        sa.Column("theme_color", sa.String(length=20), nullable=False, server_default="#2563eb"),
        sa.Column("position", sa.String(length=40), nullable=False, server_default="bottom-left"),
        sa.Column("display_delay", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_widgets_user_id", "widgets", ["user_id"])

    op.create_table(
        "widget_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("widget_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_name", sa.String(length=200), nullable=False),
        sa.Column("customer_location", sa.String(length=160), nullable=True),
        sa.Column("action_text", sa.String(length=300), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("review_text", sa.Text(), nullable=True),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["widget_id"], ["widgets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_widget_events_widget_id", "widget_events", ["widget_id"])

    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("razorpay_subscription_id", sa.String(length=160), nullable=True),
        sa.Column("plan_name", sa.String(length=30), nullable=False, server_default="free"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="active"),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("razorpay_subscription_id", name="uq_subscriptions_razorpay_subscription_id"),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_index("ix_widget_events_widget_id", table_name="widget_events")
    op.drop_table("widget_events")
    op.drop_index("ix_widgets_user_id", table_name="widgets")
    op.drop_table("widgets")
