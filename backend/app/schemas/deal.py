from pydantic import BaseModel


class DealDTO(BaseModel):
    id: int
    product_id: str
    product_name: str
    product_slug: str
    product_image: str | None
    current_price: float
    currency: str
    deal_type: str
    label: str
    discount_percent: int
    coupon_code: str | None
    cashback_amount: float | None
    valid_until: str | None


class DealsResponse(BaseModel):
    today_deals: list[DealDTO]
    festival_offers: list[DealDTO]
    cashback_deals: list[DealDTO]
    coupon_deals: list[DealDTO]
    trending: list[DealDTO]
    ai_recommended: list[DealDTO]
