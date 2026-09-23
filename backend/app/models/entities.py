import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, JSON, Numeric, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    mobile_number: Mapped[str | None] = mapped_column(String(15), unique=True, index=True, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(15), nullable=True)
    shipping_address: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    seller_profile: Mapped["SellerProfile | None"] = relationship(back_populates="user", uselist=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (Index("ix_refresh_tokens_hash", "token_hash"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class OtpChallenge(Base):
    __tablename__ = "otp_challenges"
    __table_args__ = (Index("ix_otp_challenges_mobile_created", "mobile_number", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mobile_number: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    request_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_user_read", "user_id", "is_read"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="notifications")
    
class SellerType(str, enum.Enum):
    OWNER = "OWNER"
    AUTHORIZED_REPRESENTATIVE = "AUTHORIZED_REPRESENTATIVE"

class PropertyType(str, enum.Enum):
    APARTMENT = "APARTMENT"
    INDEPENDENT_HOUSE = "INDEPENDENT_HOUSE"
    VILLA = "VILLA"
    RESIDENTIAL_PLOT = "RESIDENTIAL_PLOT"

class PropertyStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"
    LIVE = "LIVE"
    SUSPENDED = "SUSPENDED"
    SOLD = "SOLD"
    WITHDRAWN = "WITHDRAWN"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"

class LocationType(str, enum.Enum):
    CITY = "CITY"
    ZONE = "ZONE"
    LOCALITY = "LOCALITY"

class VerificationStatus(str, enum.Enum):
    NOT_REVIEWED = "NOT_REVIEWED"
    CONTACT_VERIFIED = "CONTACT_VERIFIED"
    RELATIONSHIP_REVIEWED = "RELATIONSHIP_REVIEWED"
    DOCUMENT_EVIDENCE_REVIEWED = "DOCUMENT_EVIDENCE_REVIEWED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"

class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    FOLLOW_UP = "FOLLOW_UP"
    VISITED = "VISITED"
    CLOSED = "CLOSED"

class MediaType(str, enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"

class MediaStatus(str, enum.Enum):
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    REJECTED = "REJECTED"
    DELETED = "DELETED"

class VerificationMethod(str, enum.Enum):
    CONTACT = "CONTACT"
    OWNER_DECLARATION = "OWNER_DECLARATION"
    AUTHORIZATION_REVIEW = "AUTHORIZATION_REVIEW"
    DOCUMENT_REVIEW = "DOCUMENT_REVIEW"

class EnquirySource(str, enum.Enum):
    WEBSITE = "WEBSITE"
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    WHATSAPP = "WHATSAPP"
    DIRECT = "DIRECT"
    QR = "QR"
    OTHER = "OTHER"

class ContactMethod(str, enum.Enum):
    PHONE = "PHONE"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"

class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class SocialPlatform(str, enum.Enum):
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    WHATSAPP = "WHATSAPP"

class SocialPostType(str, enum.Enum):
    POST = "POST"
    CAROUSEL = "CAROUSEL"
    REEL = "REEL"
    STORY = "STORY"
    SHARE_CARD = "SHARE_CARD"

class SocialPostStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    REMOVED = "REMOVED"

class AdminReviewDecision(str, enum.Enum):
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"
    REINSTATED = "REINSTATED"

class SellerProfile(Base):
    __tablename__ = "seller_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    seller_type: Mapped[SellerType] = mapped_column(String(32), nullable=False)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    whatsapp_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False, default=VerificationStatus.NOT_REVIEWED.value)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="seller_profile")
    properties: Mapped[list["Property"]] = relationship(back_populates="seller_profile", cascade="all, delete-orphan")

class Location(Base):
    __tablename__ = "locations"
    __table_args__ = (
        Index("ix_locations_type_active", "location_type", "is_active"),
        UniqueConstraint("parent_id", "normalized_name", name="uq_locations_parent_normalized_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), nullable=False, index=True)
    location_type: Mapped[LocationType] = mapped_column(String(24), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(140), nullable=False)
    city_name: Mapped[str] = mapped_column(String(120), nullable=False, default="Bengaluru")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    parent: Mapped["Location | None"] = relationship(remote_side="Location.id", back_populates="children")
    children: Mapped[list["Location"]] = relationship(back_populates="parent", cascade="all, delete-orphan")
    properties: Mapped[list["Property"]] = relationship(back_populates="location")

class Property(Base):
    __tablename__ = "properties"
    __table_args__ = (
        Index("ix_properties_status_type", "status", "property_type"),
        Index("ix_properties_status_location", "status", "location_id"),
        Index("ix_properties_status_price", "status", "price_amount"),
        Index("ix_properties_seller_status", "seller_profile_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    seller_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("seller_profiles.id", ondelete="CASCADE"), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("locations.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    property_type: Mapped[PropertyType] = mapped_column(String(32), nullable=False)
    listing_purpose: Mapped[str] = mapped_column(String(16), nullable=False, default="SALE")
    price_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    built_up_area_sqft: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    carpet_area_sqft: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    plot_area_sqft: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    bhk: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    floor_number: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    total_floors: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    property_age_years: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    facing: Mapped[str | None] = mapped_column(String(32), nullable=True)
    parking_details: Mapped[str | None] = mapped_column(String(160), nullable=True)
    maintenance_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    possession_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    road_width_ft: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    plot_dimensions: Mapped[str | None] = mapped_column(String(120), nullable=True)
    corner_site: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    approval_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    amenities: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    address_line: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_visibility: Mapped[str] = mapped_column(String(24), nullable=False, default="LOCALITY_ONLY")
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    status: Mapped[PropertyStatus] = mapped_column(String(32), nullable=False, default=PropertyStatus.DRAFT.value)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    seller_profile: Mapped[SellerProfile] = relationship(back_populates="properties")
    location: Mapped[Location] = relationship(back_populates="properties")
    media: Mapped[list["PropertyMedia"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    verification: Mapped["PropertyVerification | None"] = relationship(back_populates="property", uselist=False, cascade="all, delete-orphan")
    enquiries: Mapped[list["PropertyEnquiry"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    campaigns: Mapped[list["PropertyCampaign"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    reviews: Mapped[list["AdminReview"]] = relationship(back_populates="property", cascade="all, delete-orphan")


class PropertyMedia(Base):
    __tablename__ = "property_media"
    __table_args__ = (Index("ix_property_media_property_status_order", "property_id", "status", "sort_order"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    media_type: Mapped[str] = mapped_column(String(16), nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    public_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_cover: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    caption: Mapped[str | None] = mapped_column(String(240), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="UPLOADING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    property: Mapped["Property"] = relationship(back_populates="media")


class PropertyVerification(Base):
    __tablename__ = "property_verifications"
    __table_args__ = (Index("ix_property_verifications_status_expiry", "verification_status", "expires_at"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, unique=True)
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False, default=VerificationStatus.NOT_REVIEWED.value)
    verification_method: Mapped[str | None] = mapped_column(String(64), nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    property: Mapped["Property"] = relationship(back_populates="verification")


class PropertyCampaign(Base):
    __tablename__ = "property_campaigns"
    __table_args__ = (Index("ix_property_campaigns_property_status", "property_id", "status"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    campaign_title: Mapped[str] = mapped_column(String(180), nullable=False)
    campaign_key: Mapped[str] = mapped_column(String(120), nullable=False)
    campaign_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(24), nullable=False, default="INSTAGRAM")
    medium: Mapped[str] = mapped_column(String(64), nullable=False, default="social")
    content: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="DRAFT")
    public_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    property: Mapped["Property"] = relationship(back_populates="campaigns")
    social_posts: Mapped[list["SocialPost"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class SocialPost(Base):
    __tablename__ = "social_posts"
    __table_args__ = (Index("ix_social_posts_campaign_platform", "campaign_id", "platform"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("property_campaigns.id", ondelete="CASCADE"), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    post_type: Mapped[str] = mapped_column(String(24), nullable=False)
    headline: Mapped[str | None] = mapped_column(String(180), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cta: Mapped[str | None] = mapped_column(String(120), nullable=True)
    content: Mapped[str | None] = mapped_column(String(120), nullable=True)
    asset_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="DRAFT")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    campaign: Mapped["PropertyCampaign"] = relationship(back_populates="social_posts")


class PropertyEnquiry(Base):
    __tablename__ = "property_enquiries"
    __table_args__ = (
        Index("ix_property_enquiries_property_created", "property_id", "created_at"),
        Index("ix_property_enquiries_campaign_created", "campaign_id", "created_at"),
        Index("ix_property_enquiries_source_created", "source", "created_at"),
        Index("ix_property_enquiries_status_created", "status", "created_at"),
        Index("ix_property_enquiries_phone_property_created", "buyer_phone", "property_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id"), nullable=False)
    buyer_name: Mapped[str] = mapped_column(String(160), nullable=False)
    buyer_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    buyer_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    whatsapp_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    budget_amount: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    buying_timeline: Mapped[str | None] = mapped_column(String(32), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_contact_method: Mapped[str] = mapped_column(String(24), nullable=False, default="PHONE")
    source: Mapped[str] = mapped_column(String(24), nullable=False, default="WEBSITE")
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("property_campaigns.id"), nullable=True)
    source_medium: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_content: Mapped[str | None] = mapped_column(String(120), nullable=True)
    landing_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default=LeadStatus.NEW.value)
    consent_to_share: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    spam_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("property_enquiries.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    property: Mapped["Property"] = relationship(back_populates="enquiries")
    duplicate_of: Mapped["PropertyEnquiry | None"] = relationship(remote_side=[id])
    status_history: Mapped[list["LeadStatusHistory"]] = relationship(back_populates="enquiry", cascade="all, delete-orphan")


class LeadStatusHistory(Base):
    __tablename__ = "lead_status_history"
    __table_args__ = (Index("ix_lead_status_history_enquiry_created", "enquiry_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enquiry_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("property_enquiries.id", ondelete="CASCADE"), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(24), nullable=True)
    new_status: Mapped[str] = mapped_column(String(24), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    enquiry: Mapped["PropertyEnquiry"] = relationship(back_populates="status_history")


class AdminReview(Base):
    __tablename__ = "admin_reviews"
    __table_args__ = (Index("ix_admin_reviews_property_created", "property_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id"), nullable=False)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    property: Mapped["Property"] = relationship(back_populates="reviews")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity_created", "entity_type", "entity_id", "created_at"),
        Index("ix_audit_logs_actor_created", "actor_user_id", "created_at"),
        Index("ix_audit_logs_action_created", "action", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
