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


class EntitlementResponse(BaseModel):
    plan: str
    status: str
    active: bool
    is_trial: bool
    trial_ends_at: datetime | None
    max_widgets: int | None
    monthly_view_limit: int | None
    features: list[str]
    subscription_id: str | None = None
    current_period_end: datetime | None = None
    cancel_at_period_end: bool = False


class SubscriptionCancelResponse(BaseModel):
    status: str
    access_until: datetime | None
