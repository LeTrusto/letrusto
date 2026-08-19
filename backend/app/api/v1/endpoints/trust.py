from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.schemas.trust_public import PublicTrustResponse
from app.services.trust_public_service import PublicTrustService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}/trust", response_model=PublicTrustResponse)
def get_product_trust(product_id: str, db=Depends(get_db)) -> PublicTrustResponse:
    return PublicTrustService(db).get_product_trust(product_id)