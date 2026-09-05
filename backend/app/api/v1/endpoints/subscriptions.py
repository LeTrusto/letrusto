from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.subscriptions import SubscriptionCreateRequest, SubscriptionCreateResponse
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


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
    SubscriptionService(db).process_webhook(await request.body(), x_razorpay_signature)
    return {"status": "ok"}
