"""Add non-purchasable monetization plan configuration."""

from collections.abc import Sequence
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260923_53"
down_revision: str | None = "20260923_52"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "monetization_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("price_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("billing_period", sa.String(length=24), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("customer_purchase_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("features", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("code", name="uq_monetization_plans_code"),
    )
    op.create_index("ix_monetization_plans_code", "monetization_plans", ["code"])
    plans = sa.table(
        "monetization_plans",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("is_active", sa.Boolean()),
        sa.column("customer_purchase_enabled", sa.Boolean()),
        sa.column("features", postgresql.JSONB()),
        sa.column("sort_order", sa.Integer()),
    )
    op.bulk_insert(plans, [
        {"id": uuid4(), "code": "FREE", "name": "Free", "description": "Validation access while we learn from real properties.", "is_active": True, "customer_purchase_enabled": False, "features": ["PROPERTY_LISTING", "PUBLIC_PROPERTY_PAGE", "BUYER_ENQUIRIES", "BASIC_CAMPAIGN"], "sort_order": 1},
        {"id": uuid4(), "code": "PREMIUM", "name": "Premium", "description": "Enhanced marketing concept, not currently purchasable.", "is_active": False, "customer_purchase_enabled": False, "features": ["PROPERTY_LISTING", "PUBLIC_PROPERTY_PAGE", "BUYER_ENQUIRIES", "BASIC_CAMPAIGN", "ENHANCED_MARKETING", "FEATURED_PROPERTY", "CAMPAIGN_ANALYTICS"], "sort_order": 2},
        {"id": uuid4(), "code": "BUSINESS", "name": "Business", "description": "Multi-property marketing concept, not currently purchasable.", "is_active": False, "customer_purchase_enabled": False, "features": ["PROPERTY_LISTING", "PUBLIC_PROPERTY_PAGE", "BUYER_ENQUIRIES", "BASIC_CAMPAIGN", "ENHANCED_MARKETING", "FEATURED_PROPERTY", "CAMPAIGN_ANALYTICS", "MULTI_PROPERTY", "ADVANCED_CAMPAIGNS"], "sort_order": 3},
    ])


def downgrade() -> None:
    op.drop_index("ix_monetization_plans_code", table_name="monetization_plans")
    op.drop_table("monetization_plans")