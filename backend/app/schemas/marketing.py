from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

class MarketingSpendCreate(BaseModel):
    spend_date: date
    channel: str = Field(min_length=1, max_length=40)
    campaign: str | None = Field(default=None, max_length=200)
    spend_amount: Decimal = Field(ge=0, decimal_places=2, max_digits=12)
    currency: str = Field(default="INR", pattern="^INR$")
    notes: str | None = Field(default=None, max_length=500)

class MarketingSpendDTO(MarketingSpendCreate):
    id: UUID
    created_at: str
    updated_at: str

class MarketingCACRow(BaseModel):
    channel: str
    campaign: str | None
    spend: Decimal
    attributed_orders: int
    attributed_sales: Decimal
    attributed_cac: Decimal | None
    blended_cac: Decimal | None
    roas: Decimal | None
    cac_status: str

class MarketingCACResponse(BaseModel):
    spend: Decimal
    attributed_orders: int
    attributed_cac: Decimal | None
    blended_cac: Decimal | None
    target_cac: Decimal
    actual_cac_status: str
    rows: list[MarketingCACRow]

class AttributionCreate(BaseModel):
    order_id: UUID
    channel: str = Field(min_length=1, max_length=40)
    campaign: str | None = Field(default=None, max_length=200)
    attribution_method: str = Field(min_length=1, max_length=40)

class AttributionDTO(AttributionCreate):
    id: UUID
    status: str
    created_at: str


class MarketingLeadCreate(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    full_name: str | None = Field(default=None, max_length=200)
    business_type: str = Field(min_length=1, max_length=60)
    primary_goal: str = Field(min_length=1, max_length=60)
    monthly_visitors: str = Field(min_length=1, max_length=40)
    recommended_widget: str = Field(min_length=1, max_length=60)
    source: str = Field(default="widget_quiz", min_length=1, max_length=80)
    consented_to_updates: bool = False


class MarketingLeadResponse(BaseModel):
    message: str
    recommended_widget: str
