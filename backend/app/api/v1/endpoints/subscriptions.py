import logging

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Subscription, User
from app.schemas.subscriptions import EntitlementResponse, SubscriptionCancelResponse, SubscriptionCreateRequest, SubscriptionCreateResponse
from app.services.entitlement_service import get_entitlement
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
logger = logging.getLogger(__name__)


@router.get("/status", response_model=EntitlementResponse)
def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EntitlementResponse:
    entitlement = get_entitlement(db, current_user)
    record = db.scalar(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc())
    )
    return EntitlementResponse(
        plan=entitlement.plan,
        status=entitlement.status,
        active=entitlement.active,
        is_trial=entitlement.is_trial,
        trial_ends_at=entitlement.trial_ends_at,
        max_widgets=entitlement.max_widgets,
        monthly_view_limit=entitlement.monthly_view_limit,
        features=sorted(entitlement.features),
        subscription_id=record.razorpay_subscription_id if record else None,
        current_period_end=record.current_period_end if record else None,
        cancel_at_period_end=record.cancel_at_period_end if record else False,
    )


@router.post("/cancel", response_model=SubscriptionCancelResponse)
def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubscriptionCancelResponse:
    return SubscriptionService(db).cancel_subscription(current_user)


@router.post("", response_model=SubscriptionCreateResponse)
def create_subscription(
    payload: SubscriptionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubscriptionCreateResponse:
    return SubscriptionService(db).create_subscription(current_user, payload.plan_name)


@router.post("/webhook", status_code=200)
async def subscription_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        SubscriptionService(db).process_webhook(await request.body(), x_razorpay_signature)
    except Exception as exc:
        logger.exception(
            "Razorpay subscription webhook failed: error_type=%s",
            type(exc).__name__,
        )
        raise
    return {"status": "ok"}
