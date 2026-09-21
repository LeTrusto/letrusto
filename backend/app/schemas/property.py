from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.entities import AdminReviewDecision, LocationType, MediaType, PropertyStatus, PropertyType, VerificationMethod, VerificationStatus


class LocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=140)
    location_type: LocationType
    parent_id: UUID | None = None
    city_name: str = Field(default="Bengaluru", max_length=120)


class LocationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    location_type: LocationType
    parent_id: UUID | None
    city_name: str


class PropertyCreate(BaseModel):
    location_id: UUID
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=1)
    property_type: PropertyType
    price_amount: Decimal = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    built_up_area_sqft: Decimal | None = Field(default=None, ge=0)
    carpet_area_sqft: Decimal | None = Field(default=None, ge=0)
    plot_area_sqft: Decimal | None = Field(default=None, ge=0)
    bhk: int | None = Field(default=None, ge=0)
    floor_number: int | None = Field(default=None, ge=0)
    total_floors: int | None = Field(default=None, ge=0)
    property_age_years: int | None = Field(default=None, ge=0)
    facing: str | None = Field(default=None, max_length=32)
    parking_details: str | None = Field(default=None, max_length=160)
    maintenance_amount: Decimal | None = Field(default=None, ge=0)
    possession_status: str | None = Field(default=None, max_length=32)
    road_width_ft: Decimal | None = Field(default=None, ge=0)
    plot_dimensions: str | None = Field(default=None, max_length=120)
    corner_site: bool | None = None
    approval_information: str | None = None
    amenities: dict | None = None
    address_line: str | None = None
    address_visibility: str = Field(default="LOCALITY_ONLY", max_length=24)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)

    @field_validator("address_visibility")
    @classmethod
    def valid_address_visibility(cls, value: str) -> str:
        if value not in {"LOCALITY_ONLY", "APPROXIMATE", "PRIVATE"}:
            raise ValueError("Invalid address visibility")
        return value


class PropertyUpdate(BaseModel):
    location_id: UUID | None = None
    title: str | None = Field(default=None, min_length=3, max_length=180)
    description: str | None = Field(default=None, min_length=1)
    property_type: PropertyType | None = None
    price_amount: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    built_up_area_sqft: Decimal | None = Field(default=None, ge=0)
    carpet_area_sqft: Decimal | None = Field(default=None, ge=0)
    plot_area_sqft: Decimal | None = Field(default=None, ge=0)
    bhk: int | None = Field(default=None, ge=0)
    floor_number: int | None = Field(default=None, ge=0)
    total_floors: int | None = Field(default=None, ge=0)
    property_age_years: int | None = Field(default=None, ge=0)
    facing: str | None = Field(default=None, max_length=32)
    parking_details: str | None = Field(default=None, max_length=160)
    maintenance_amount: Decimal | None = Field(default=None, ge=0)
    possession_status: str | None = Field(default=None, max_length=32)
    road_width_ft: Decimal | None = Field(default=None, ge=0)
    plot_dimensions: str | None = Field(default=None, max_length=120)
    corner_site: bool | None = None
    approval_information: str | None = None
    amenities: dict | None = None
    address_line: str | None = None
    address_visibility: str | None = Field(default=None, max_length=24)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)


class PropertyMediaDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    media_type: str
    storage_key: str
    public_url: str | None
    mime_type: str
    file_size_bytes: int
    sort_order: int
    is_cover: bool
    caption: str | None
    status: str


class PublicPropertyMediaDTO(BaseModel):
    id: UUID
    media_type: str
    public_url: str | None
    mime_type: str
    sort_order: int
    is_cover: bool
    caption: str | None


class PublicPropertyDTO(BaseModel):
    id: UUID
    slug: str
    title: str
    description: str
    property_type: PropertyType
    price_amount: Decimal
    currency: str
    built_up_area_sqft: Decimal | None
    carpet_area_sqft: Decimal | None
    plot_area_sqft: Decimal | None
    bhk: int | None
    floor_number: int | None
    total_floors: int | None
    facing: str | None
    parking_details: str | None
    maintenance_amount: Decimal | None
    possession_status: str | None
    plot_dimensions: str | None
    corner_site: bool | None
    address_visibility: str
    status: PropertyStatus
    published_at: datetime | None
    location: LocationDTO
    media: list[PublicPropertyMediaDTO]
    verification_label: str


class SellerPropertyDTO(PublicPropertyDTO):
    seller_profile_id: UUID
    address_line: str | None
    approval_information: str | None
    created_at: datetime
    updated_at: datetime
    status: PropertyStatus


class PropertySubmitResponse(BaseModel):
    id: UUID
    status: PropertyStatus


class AdminReviewRequest(BaseModel):
    decision: AdminReviewDecision
    notes: str | None = None


class VerificationUpdateRequest(BaseModel):
    verification_status: VerificationStatus
    verification_method: VerificationMethod | None = None
    notes: str | None = None
    expires_at: datetime | None = None


class MediaCreateRequest(BaseModel):
    media_type: MediaType
    storage_key: str = Field(min_length=1, max_length=1000)
    mime_type: str = Field(min_length=1, max_length=120)
    file_size_bytes: int = Field(gt=0)
    is_cover: bool = False
    caption: str | None = Field(default=None, max_length=240)
