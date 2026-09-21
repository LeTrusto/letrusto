"""Bangalore pivot: clean schema baseline retaining only generic auth/notification tables

Revision ID: 20260921_46
Revises: 20260908_44

This migration performs the full LeTrusto -> Bangalore Property pivot cleanup.
It drops every old business table (ecommerce, SaaS, AI tools, trust/reviews,
subscriptions, digital products, and the experimental property scaffold) and
recreates only the six genuinely generic tables the new application needs.

Historical migration files before this one are intentionally left untouched
as an auditable record of the old schema's evolution. The experimental
property-scaffold migration is not part of that historical record and was
removed rather than kept, per the explicit pivot cleanup instructions.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260921_46"
down_revision: str | None = "20260908_44"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_OLD_TABLES = (
    "property_contact_unlocks", "property_payment_attempts", "property_listings",
    "order_marketing_attribution", "marketing_spend", "inventory_reservations", "refund_requests",
    "trust_audit_events", "trust_verifications", "trust_claim_evidence", "trust_evidence", "trust_claims",
    "price_alerts", "saved_comparisons",
    "marketing_leads", "widget_usage", "subscription_webhook_events", "subscriptions",
    "widget_events", "widgets",
    "digital_entitlements", "digital_payment_attempts", "payment_attempts", "order_items", "orders",
    "cart_items", "carts",
    "favorites", "product_similarities", "articles", "product_buy_links", "reviews", "price_history",
    "product_tags", "product_not_recommended_for", "product_best_for", "product_cons", "product_pros",
    "product_features", "product_specifications", "product_images", "product_market_evidence",
    "operational_alert_states", "supplier_variant_inventory", "product_variants",
    "printful_shipping_rates", "products", "supplier_candidates", "ai_tool_fact_provenance", "ai_tools",
    "ai_tool_categories", "brands", "categories", "ai_conversations", "ai_messages", "analytics_events",
    "support_tickets", "deals",
)


def upgrade() -> None:
    for table in _OLD_TABLES:
        op.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')

    op.drop_table("notifications")
    op.drop_table("otp_challenges")
    op.drop_table("email_verification_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("users")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=True, unique=True),
        sa.Column("mobile_number", sa.String(length=15), nullable=True, unique=True),
        sa.Column("phone_number", sa.String(length=15), nullable=True),
        sa.Column("shipping_address", sa.JSON(), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("google_id", sa.String(length=120), nullable=True, unique=True),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_mobile_number", "users", ["mobile_number"])
    op.create_index("ix_users_google_id", "users", ["google_id"])

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token_hash", sa.String(length=255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_refresh_tokens_hash", "refresh_tokens", ["token_hash"])

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token_hash", sa.String(length=64), nullable=False, unique=True, index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "email_verification_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token_hash", sa.String(length=64), nullable=False, unique=True, index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "otp_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mobile_number", sa.String(length=15), nullable=False, index=True),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("request_ip", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_otp_challenges_mobile_created", "otp_challenges", ["mobile_number", "created_at"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_read", "notifications", ["user_id", "is_read"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("otp_challenges")
    op.drop_table("email_verification_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
