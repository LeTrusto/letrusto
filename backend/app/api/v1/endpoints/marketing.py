from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.entities import MarketingLead
from app.schemas.marketing import MarketingLeadCreate, MarketingLeadResponse

router = APIRouter(prefix="/marketing", tags=["marketing"])


@router.post("/leads", response_model=MarketingLeadResponse, status_code=201)
def capture_lead(payload: MarketingLeadCreate, db: Session = Depends(get_db)) -> MarketingLeadResponse:
    email = payload.email.strip().lower()
    existing = db.scalar(
        select(MarketingLead).where(MarketingLead.email == email, MarketingLead.source == payload.source)
    )
    if existing:
        existing.full_name = payload.full_name or existing.full_name
        existing.business_type = payload.business_type
        existing.primary_goal = payload.primary_goal
        existing.monthly_visitors = payload.monthly_visitors
        existing.recommended_widget = payload.recommended_widget
        existing.consented_to_updates = existing.consented_to_updates or payload.consented_to_updates
    else:
        db.add(MarketingLead(
            email=email,
            full_name=payload.full_name,
            business_type=payload.business_type,
            primary_goal=payload.primary_goal,
            monthly_visitors=payload.monthly_visitors,
            recommended_widget=payload.recommended_widget,
            source=payload.source,
            consented_to_updates=payload.consented_to_updates,
        ))
    db.commit()
    return MarketingLeadResponse(message="Your recommendation is ready.", recommended_widget=payload.recommended_widget)