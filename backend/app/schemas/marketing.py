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
