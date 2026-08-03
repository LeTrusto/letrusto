from fastapi import APIRouter, Depends

from app.api.deps import get_deal_service
from app.schemas.deal import DealsResponse
from app.services.deal_service import DealService

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=DealsResponse)
def get_deals(service: DealService = Depends(get_deal_service)) -> DealsResponse:
    return service.get_deals_with_fallback()
