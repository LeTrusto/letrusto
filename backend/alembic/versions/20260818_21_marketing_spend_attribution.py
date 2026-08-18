"""add admin marketing spend and explicit order attribution

Revision ID: 20260818_21
Revises: 20260818_20
"""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "20260818_21"
down_revision: str | None = "20260818_20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table(
        "marketing_spend",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("spend_date", sa.Date(), nullable=False),
        sa.Column("channel", sa.String(40), nullable=False),
        sa.Column("campaign", sa.String(200), nullable=True),
        sa.Column("spend_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(8), nullable=False, server_default="INR"),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.CheckConstraint("spend_amount >= 0", name="ck_marketing_spend_nonnegative"),
        sa.CheckConstraint("currency = 'INR'", name="ck_marketing_spend_currency_inr"),
    )
    op.create_index("ix_marketing_spend_date_channel", "marketing_spend", ["spend_date", "channel"])
    op.create_index("ix_marketing_spend_campaign", "marketing_spend", ["campaign"])
    op.create_table(
        "order_marketing_attribution",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(40), nullable=False),
        sa.Column("campaign", sa.String(200), nullable=True),
        sa.Column("attribution_method", sa.String(40), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ATTRIBUTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("order_id", name="uq_order_marketing_attribution_order"),
        sa.CheckConstraint("status IN ('ATTRIBUTED', 'UNATTRIBUTED', 'UNKNOWN')", name="ck_order_marketing_attribution_status"),
    )
    op.create_index("ix_order_marketing_attribution_channel_campaign", "order_marketing_attribution", ["channel", "campaign"])

def downgrade() -> None:
    op.drop_index("ix_order_marketing_attribution_channel_campaign", table_name="order_marketing_attribution")
    op.drop_table("order_marketing_attribution")
    op.drop_index("ix_marketing_spend_campaign", table_name="marketing_spend")
    op.drop_index("ix_marketing_spend_date_channel", table_name="marketing_spend")
    op.drop_table("marketing_spend")
