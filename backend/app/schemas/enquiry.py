from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.entities import ContactMethod, EnquirySource, LeadStatus


class EnquiryCreate(BaseModel):
    buyer_name: str = Field(min_length=1, max_length=160)
    buyer_phone: str = Field(min_length=7, max_length=32)
    buyer_email: EmailStr | None = None
    whatsapp_available: bool = False
    budget_amount: Decimal | None = Field(default=None, ge=0)
    buying_timeline: str | None = Field(default=None, max_length=32)
    message: str | None = None
    preferred_contact_method: ContactMethod = ContactMethod.PHONE
    source: EnquirySource = EnquirySource.WEBSITE
    campaign_id: UUID | None = None
    source_medium: str | None = Field(default=None, max_length=64)
    source_content: str | None = Field(default=None, max_length=120)
    landing_path: str | None = None
    consent_to_share: bool


class PublicEnquiryResponse(BaseModel):
    id: UUID
    property_id: UUID
    status: LeadStatus
    created_at: datetime


class SellerEnquiryDTO(BaseModel):
    id: UUID
    property_id: UUID
    buyer_name: str
    buyer_phone: str
    buyer_email: EmailStr | None
    whatsapp_available: bool
    budget_amount: Decimal | None
    buying_timeline: str | None
    message: str | None
    preferred_contact_method: ContactMethod
    source: EnquirySource
    status: LeadStatus
    created_at: datetime


class LeadStatusUpdate(BaseModel):
    status: LeadStatus
    note: str | None = Field(default=None, max_length=500)
