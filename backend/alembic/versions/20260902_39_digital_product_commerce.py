"""add isolated digital product commerce tables

Revision ID: 20260902_39
Revises: 20260901_38
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260902_39"
down_revision: str | None = "20260901_38"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "digital_payment_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_slug", sa.String(length=160), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("provider_order_id", sa.String(length=120), nullable=False),
        sa.Column("provider_payment_id", sa.String(length=160), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("failure_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_order_id", name="uq_digital_payment_attempt_provider_order"),
        sa.UniqueConstraint("provider", "provider_payment_id", name="uq_digital_payment_attempt_provider_payment"),
    )
    op.create_index("ix_digital_payment_attempts_user_id", "digital_payment_attempts", ["user_id"])
    op.create_index("ix_digital_payment_attempts_product_slug", "digital_payment_attempts", ["product_slug"])
    op.create_index("ix_digital_payment_attempts_status", "digital_payment_attempts", ["status"])
    op.create_table(
        "digital_entitlements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_attempt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_slug", sa.String(length=160), nullable=False),
        sa.Column("download_count", sa.Integer(), nullable=False),
        sa.Column("last_downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["payment_attempt_id"], ["digital_payment_attempts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_attempt_id"),
        sa.UniqueConstraint("user_id", "product_slug", name="uq_digital_entitlement_user_product"),
    )
    op.create_index("ix_digital_entitlements_user_id", "digital_entitlements", ["user_id"])
    op.create_index("ix_digital_entitlements_product_slug", "digital_entitlements", ["product_slug"])


def downgrade() -> None:
    op.drop_index("ix_digital_entitlements_product_slug", table_name="digital_entitlements")
    op.drop_index("ix_digital_entitlements_user_id", table_name="digital_entitlements")
    op.drop_table("digital_entitlements")
    op.drop_index("ix_digital_payment_attempts_status", table_name="digital_payment_attempts")
    op.drop_index("ix_digital_payment_attempts_product_slug", table_name="digital_payment_attempts")
    op.drop_index("ix_digital_payment_attempts_user_id", table_name="digital_payment_attempts")
    op.drop_table("digital_payment_attempts")
