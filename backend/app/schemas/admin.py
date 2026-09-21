from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.property import LocationDTO


class AdminMediaDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    media_type: str
    public_url: str | None
    mime_type: str
    sort_order: int
    is_cover: bool
    caption: str | None
    status: str


class AdminSellerDTO(BaseModel):
    id: UUID
    display_name: str
    seller_type: str
    phone: str
    email: str | None
    whatsapp_available: bool
    verification_status: str
    property_count: int | None = None
    created_at: datetime | None = None


class AdminVerificationDTO(BaseModel):
    verification_status: str
    verification_method: str | None
    notes: str | None
    verified_by: UUID | None
    verified_at: datetime | None
    expires_at: datetime | None


class AdminReviewDTO(BaseModel):
    id: UUID
    decision: str
    notes: str | None
    reviewer_id: UUID
    reviewer_name: str | None
    created_at: datetime


class AdminAuditDTO(BaseModel):
    id: UUID
    action: str
    metadata: dict | None
    actor_user_id: UUID | None
    created_at: datetime


class AdminPropertyDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    description: str
    property_type: str
    price_amount: Decimal
    currency: str
    built_up_area_sqft: Decimal | None
    carpet_area_sqft: Decimal | None
    plot_area_sqft: Decimal | None
    bhk: int | None
    floor_number: int | None
    total_floors: int | None
    property_age_years: int | None
    facing: str | None
    parking_details: str | None
    maintenance_amount: Decimal | None
    possession_status: str | None
    road_width_ft: Decimal | None
    plot_dimensions: str | None
    corner_site: bool | None
    approval_information: str | None
    amenities: dict | None
    address_line: str | None
    address_visibility: str
    latitude: Decimal | None
    longitude: Decimal | None
    status: str
    submitted_at: datetime | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    location: LocationDTO
    media: list[AdminMediaDTO]
    seller: AdminSellerDTO
    verification: AdminVerificationDTO | None
    reviews: list[AdminReviewDTO]
    audit: list[AdminAuditDTO]


class AdminEnquiryDTO(BaseModel):
    id: UUID
    property_id: UUID
    property_title: str
    seller_name: str
    buyer_name: str
    buyer_phone: str
    buyer_email: str | None
    whatsapp_available: bool
    budget_amount: Decimal | None
    buying_timeline: str | None
    message: str | None
    preferred_contact_method: str
    source: str
    status: str
    consent_to_share: bool
    created_at: datetime


class AdminDashboardDTO(BaseModel):
    awaiting_review: int
    changes_requested: int
    live_properties: int
    suspended_properties: int
    recent_enquiries: list[AdminEnquiryDTO]
