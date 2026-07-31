from fastapi import APIRouter, Depends

from app.api.deps import get_product_service
from app.schemas.product import CompareResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["compare"])


@router.get("/compare", response_model=CompareResponse)
def compare_products(
    first: str | None = None,
    second: str | None = None,
    service: ProductService = Depends(get_product_service),
) -> CompareResponse:
    return service.get_compare(first, second)
