from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update

from app.api.deps import get_optional_user, get_analytics_service
from app.db.session import SessionLocal
from app.models.entities import ProductBuyLink
from app.schemas.analytics import AnalyticsEventRequest
from app.schemas.common import MessageResponse

from fastapi import Depends
from app.models.entities import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/affiliate", tags=["affiliate"])


@router.post("/click/{link_id}", status_code=202, response_model=MessageResponse)
def record_affiliate_click(
    link_id: int,
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User | None = Depends(get_optional_user),
) -> MessageResponse:
    """Record an affiliate click and increment the counter. Returns 202 so the frontend can fire-and-forget."""
    db = SessionLocal()
    try:
        link = db.scalars(select(ProductBuyLink).where(ProductBuyLink.id == link_id)).first()
        if link:
            db.execute(
                update(ProductBuyLink)
                .where(ProductBuyLink.id == link_id)
                .values(click_count=ProductBuyLink.click_count + 1)
            )
            db.commit()
            service.record_event(
                AnalyticsEventRequest(
                    event_type="buy_click",
                    product_id=str(link.product_id),
                    payload={"link_id": link_id, "label": link.label, "retailer_type": link.retailer_type},
                ),
                user_id=current_user.id if current_user else None,
            )
    finally:
        db.close()
    return MessageResponse(message="Click recorded")
