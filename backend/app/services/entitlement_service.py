"""Backend source of truth for SaaS plan access and usage limits."""

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Subscription, User


@dataclass(frozen=True)
class Entitlement:
    plan: str
    status: str
    active: bool
    is_trial: bool
    trial_ends_at: datetime | None
    max_widgets: int | None
    monthly_view_limit: int | None
    features: frozenset[str]


PLAN_LIMITS = {
    "free": (1, 1_000, frozenset({"live_sales_popups"})),
    "starter": (3, 10_000, frozenset({"live_sales_popups", "custom_colors", "review_collection"})),
    "pro": (None, None, frozenset({"live_sales_popups", "custom_colors", "review_collection", "video_reviews"})),
}


def get_entitlement(db: Session, user: User) -> Entitlement:
    now = datetime.now(timezone.utc)
    subscription = db.scalar(
        select(Subscription)
        .where(Subscription.user_id == user.id)
        .order_by(Subscription.created_at.desc())
    )
    if subscription and subscription.plan_name in {"starter", "pro"}:
        paid_active = subscription.status in {"created", "pending", "authenticated", "active", "cancellation_pending"}
        period_active = subscription.current_period_end is None or _as_utc(subscription.current_period_end) > now
        grace_active = subscription.grace_until is not None and _as_utc(subscription.grace_until) > now
        if paid_active and (period_active or grace_active):
            return _build(subscription.plan_name, subscription.status, True, False, user.trial_ends_at)

    trial_end = _as_utc(user.trial_ends_at) if user.trial_ends_at else None
    if trial_end and trial_end > now:
        return _build("starter", "trialing", True, True, trial_end)
    return _build("free", "free", True, False, trial_end)


def _build(plan: str, status: str, active: bool, is_trial: bool, trial_ends_at: datetime | None) -> Entitlement:
    max_widgets, monthly_view_limit, features = PLAN_LIMITS[plan]
    return Entitlement(plan, status, active, is_trial, trial_ends_at, max_widgets, monthly_view_limit, features)


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value