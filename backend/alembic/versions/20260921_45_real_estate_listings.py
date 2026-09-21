"""real estate property listings, payment attempts, and contact unlocks

Revision ID: 20260921_45
Revises: 20260908_44
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260921_45"
down_revision: str | None = "20260908_44"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "property_listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("seller_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("property_type", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("locality", sa.String(length=160), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False, server_default="Bangalore"),
        sa.Column("price", sa.Numeric(14, 2), nullable=False),
        sa.Column("area_sqft", sa.Numeric(10, 2), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("image_urls", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("contact_name", sa.String(length=200), nullable=False),
        sa.Column("contact_phone", sa.String(length=20), nullable=False),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING_PAYMENT"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("moderation_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_property_listings_status_type", "property_listings", ["status", "property_type"])
    op.create_index("ix_property_listings_locality", "property_listings", ["locality"])

    op.create_table(
        "property_payment_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("property_listings.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("purpose", sa.String(length=20), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False, server_default="RAZORPAY"),
        sa.Column("provider_order_id", sa.String(length=120), nullable=False),
        sa.Column("provider_payment_id", sa.String(length=160), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="INR"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("provider_order_id", name="uq_property_payment_provider_order"),
        sa.UniqueConstraint("provider", "provider_payment_id", name="uq_property_payment_provider_payment"),
    )

    op.create_table(
        "property_contact_unlocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("property_listings.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("buyer_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("payment_attempt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("property_payment_attempts.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("listing_id", "buyer_user_id", name="uq_property_unlock_listing_buyer"),
    )


def downgrade() -> None:
    op.drop_table("property_contact_unlocks")
    op.drop_table("property_payment_attempts")
    op.drop_index("ix_property_listings_locality", table_name="property_listings")
    op.drop_index("ix_property_listings_status_type", table_name="property_listings")
    op.drop_table("property_listings")
