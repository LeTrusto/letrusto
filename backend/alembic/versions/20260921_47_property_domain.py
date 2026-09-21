"""Add Bangalore property domain tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260921_47"
down_revision: str | None = "20260921_46"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_col(name: str, *args, **kwargs):
    return sa.Column(name, postgresql.UUID(as_uuid=True), *args, **kwargs)


def timestamps():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def upgrade() -> None:
    op.create_table("seller_profiles", uuid_col("id", primary_key=True), uuid_col("user_id", sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("seller_type", sa.String(32), nullable=False), sa.Column("display_name", sa.String(160), nullable=False), sa.Column("phone", sa.String(32), nullable=False), sa.Column("whatsapp_available", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("email", sa.String(320)), sa.Column("verification_status", sa.String(32), nullable=False, server_default="NOT_REVIEWED"), sa.Column("internal_notes", sa.Text()), *timestamps(), sa.UniqueConstraint("user_id"))
    op.create_index("ix_seller_profiles_user_id", "seller_profiles", ["user_id"], unique=True)
    op.create_index("ix_seller_profiles_verification_status", "seller_profiles", ["verification_status"])
    op.create_table("locations", uuid_col("id", primary_key=True), uuid_col("parent_id", sa.ForeignKey("locations.id", ondelete="CASCADE")), sa.Column("name", sa.String(120), nullable=False), sa.Column("slug", sa.String(140), nullable=False), sa.Column("location_type", sa.String(24), nullable=False), sa.Column("normalized_name", sa.String(140), nullable=False), sa.Column("city_name", sa.String(120), nullable=False, server_default="Bengaluru"), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("latitude", sa.Numeric(9, 6)), sa.Column("longitude", sa.Numeric(9, 6)), sa.UniqueConstraint("parent_id", "normalized_name", name="uq_locations_parent_normalized_name"), *timestamps())
    op.create_index("ix_locations_parent_id", "locations", ["parent_id"])
    op.create_index("ix_locations_type_active", "locations", ["location_type", "is_active"])
    op.create_index("ix_locations_slug", "locations", ["slug"])
    op.create_table("properties", uuid_col("id", primary_key=True), sa.Column("slug", sa.String(180), nullable=False, unique=True), uuid_col("seller_profile_id", sa.ForeignKey("seller_profiles.id", ondelete="CASCADE"), nullable=False), uuid_col("location_id", sa.ForeignKey("locations.id"), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("property_type", sa.String(32), nullable=False), sa.Column("listing_purpose", sa.String(16), nullable=False, server_default="SALE"), sa.Column("price_amount", sa.Numeric(14, 2), nullable=False), sa.Column("currency", sa.String(3), nullable=False, server_default="INR"), sa.Column("built_up_area_sqft", sa.Numeric(12, 2)), sa.Column("carpet_area_sqft", sa.Numeric(12, 2)), sa.Column("plot_area_sqft", sa.Numeric(12, 2)), sa.Column("bhk", sa.SmallInteger()), sa.Column("floor_number", sa.SmallInteger()), sa.Column("total_floors", sa.SmallInteger()), sa.Column("property_age_years", sa.SmallInteger()), sa.Column("facing", sa.String(32)), sa.Column("parking_details", sa.String(160)), sa.Column("maintenance_amount", sa.Numeric(12, 2)), sa.Column("possession_status", sa.String(32)), sa.Column("road_width_ft", sa.Numeric(8, 2)), sa.Column("plot_dimensions", sa.String(120)), sa.Column("corner_site", sa.Boolean()), sa.Column("approval_information", sa.Text()), sa.Column("amenities", postgresql.JSONB()), sa.Column("address_line", sa.Text()), sa.Column("address_visibility", sa.String(24), nullable=False, server_default="LOCALITY_ONLY"), sa.Column("latitude", sa.Numeric(9, 6)), sa.Column("longitude", sa.Numeric(9, 6)), sa.Column("status", sa.String(32), nullable=False, server_default="DRAFT"), sa.Column("submitted_at", sa.DateTime(timezone=True)), sa.Column("published_at", sa.DateTime(timezone=True)), sa.Column("expires_at", sa.DateTime(timezone=True)), *timestamps())
    for name, cols in [("status_type", ["status", "property_type"]), ("status_location", ["status", "location_id"]), ("status_price", ["status", "price_amount"]), ("seller_status", ["seller_profile_id", "status"])]: op.create_index(f"ix_properties_{name}", "properties", cols)
    op.create_index("ix_properties_slug", "properties", ["slug"], unique=True)
    op.create_table("property_media", uuid_col("id", primary_key=True), uuid_col("property_id", sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False), sa.Column("media_type", sa.String(16), nullable=False), sa.Column("storage_key", sa.Text(), nullable=False), sa.Column("public_url", sa.Text()), sa.Column("mime_type", sa.String(120), nullable=False), sa.Column("file_size_bytes", sa.BigInteger(), nullable=False), sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"), sa.Column("is_cover", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("caption", sa.String(240)), sa.Column("status", sa.String(24), nullable=False, server_default="UPLOADING"), *timestamps())
    op.create_index("ix_property_media_property_status_order", "property_media", ["property_id", "status", "sort_order"])
    op.create_index("uq_property_media_active_cover", "property_media", ["property_id"], unique=True, postgresql_where=sa.text("is_cover = true AND status <> 'DELETED'"))
    op.create_table("property_verifications", uuid_col("id", primary_key=True), uuid_col("property_id", sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False), sa.Column("verification_status", sa.String(32), nullable=False, server_default="NOT_REVIEWED"), sa.Column("verification_method", sa.String(64)), uuid_col("verified_by", sa.ForeignKey("users.id")), sa.Column("verified_at", sa.DateTime(timezone=True)), sa.Column("expires_at", sa.DateTime(timezone=True)), sa.Column("notes", sa.Text()), *timestamps(), sa.UniqueConstraint("property_id"))
    op.create_index("ix_property_verifications_status_expiry", "property_verifications", ["verification_status", "expires_at"])
    op.create_table("property_campaigns", uuid_col("id", primary_key=True), uuid_col("property_id", sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False), sa.Column("campaign_title", sa.String(180), nullable=False), sa.Column("campaign_description", sa.Text()), sa.Column("status", sa.String(24), nullable=False, server_default="DRAFT"), sa.Column("public_path", sa.Text()), sa.Column("start_at", sa.DateTime(timezone=True)), sa.Column("end_at", sa.DateTime(timezone=True)), *timestamps())
    op.create_index("ix_property_campaigns_property_status", "property_campaigns", ["property_id", "status"])
    op.create_index("uq_property_campaigns_active", "property_campaigns", ["property_id"], unique=True, postgresql_where=sa.text("status = 'ACTIVE'"))
    op.create_table("social_posts", uuid_col("id", primary_key=True), uuid_col("campaign_id", sa.ForeignKey("property_campaigns.id", ondelete="CASCADE"), nullable=False), sa.Column("platform", sa.String(20), nullable=False), sa.Column("post_type", sa.String(24), nullable=False), sa.Column("asset_url", sa.Text()), sa.Column("published_url", sa.Text()), sa.Column("status", sa.String(24), nullable=False, server_default="DRAFT"), sa.Column("published_at", sa.DateTime(timezone=True)), *timestamps())
    op.create_index("ix_social_posts_campaign_platform", "social_posts", ["campaign_id", "platform"])
    op.create_table("property_enquiries", uuid_col("id", primary_key=True), uuid_col("property_id", sa.ForeignKey("properties.id"), nullable=False), sa.Column("buyer_name", sa.String(160), nullable=False), sa.Column("buyer_phone", sa.String(32), nullable=False), sa.Column("buyer_email", sa.String(320)), sa.Column("whatsapp_available", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("budget_amount", sa.Numeric(14, 2)), sa.Column("buying_timeline", sa.String(32)), sa.Column("message", sa.Text()), sa.Column("preferred_contact_method", sa.String(24), nullable=False, server_default="PHONE"), sa.Column("source", sa.String(24), nullable=False, server_default="WEBSITE"), uuid_col("campaign_id", sa.ForeignKey("property_campaigns.id")), sa.Column("source_medium", sa.String(64)), sa.Column("source_content", sa.String(120)), sa.Column("landing_path", sa.Text()), sa.Column("status", sa.String(24), nullable=False, server_default="NEW"), sa.Column("consent_to_share", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("consent_at", sa.DateTime(timezone=True)), sa.Column("spam_flag", sa.Boolean(), nullable=False, server_default=sa.false()), uuid_col("duplicate_of_id", sa.ForeignKey("property_enquiries.id")), *timestamps())
    for name, cols in [("property_created", ["property_id", "created_at"]), ("campaign_created", ["campaign_id", "created_at"]), ("source_created", ["source", "created_at"]), ("status_created", ["status", "created_at"]), ("phone_property_created", ["buyer_phone", "property_id", "created_at"])]: op.create_index(f"ix_property_enquiries_{name}", "property_enquiries", cols)
    op.create_table("lead_status_history", uuid_col("id", primary_key=True), uuid_col("enquiry_id", sa.ForeignKey("property_enquiries.id", ondelete="CASCADE"), nullable=False), sa.Column("old_status", sa.String(24)), sa.Column("new_status", sa.String(24), nullable=False), uuid_col("changed_by", sa.ForeignKey("users.id"), nullable=False), sa.Column("note", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_lead_status_history_enquiry_created", "lead_status_history", ["enquiry_id", "created_at"])
    op.create_table("admin_reviews", uuid_col("id", primary_key=True), uuid_col("property_id", sa.ForeignKey("properties.id"), nullable=False), uuid_col("reviewer_id", sa.ForeignKey("users.id"), nullable=False), sa.Column("decision", sa.String(32), nullable=False), sa.Column("notes", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_admin_reviews_property_created", "admin_reviews", ["property_id", "created_at"])
    op.create_table("audit_logs", uuid_col("id", primary_key=True), uuid_col("actor_user_id", sa.ForeignKey("users.id")), sa.Column("entity_type", sa.String(40), nullable=False), uuid_col("entity_id", nullable=False), sa.Column("action", sa.String(64), nullable=False), sa.Column("metadata", postgresql.JSONB()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_audit_logs_entity_created", "audit_logs", ["entity_type", "entity_id", "created_at"])
    op.create_index("ix_audit_logs_actor_created", "audit_logs", ["actor_user_id", "created_at"])
    op.create_index("ix_audit_logs_action_created", "audit_logs", ["action", "created_at"])


def downgrade() -> None:
    for table in ("audit_logs", "admin_reviews", "lead_status_history", "property_enquiries", "social_posts", "property_campaigns", "property_verifications", "property_media", "properties", "locations", "seller_profiles"):
        op.drop_table(table)
