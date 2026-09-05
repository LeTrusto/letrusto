from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SubscriptionCreateRequest(BaseModel):
    plan_name: str = Field(pattern="^(starter|pro)$")


class SubscriptionCreateResponse(BaseModel):
    subscription_id: str
    plan_name: str
    key_id: str
    status: str


class SubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    razorpay_subscription_id: str | None
    plan_name: str
    status: str
    current_period_end: datetime | None
    created_at: datetime
