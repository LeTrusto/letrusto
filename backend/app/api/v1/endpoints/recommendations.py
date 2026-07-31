from fastapi import APIRouter, Depends, Query

from app.api.deps import get_product_service
from app.schemas.product import ProductDTO
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["recommendations"])


@router.get("/recommendations", response_model=list[ProductDTO])
def get_recommendations(
    q: str,
    limit: int = Query(default=4, ge=1, le=50),
    service: ProductService = Depends(get_product_service),
) -> list[ProductDTO]:
    return service.get_recommendations(q, limit)


@router.get("/{product_id}/similar", response_model=list[ProductDTO])
def get_similar_products(
    product_id: str,
    limit: int = Query(default=4, ge=1, le=20),
    service: ProductService = Depends(get_product_service),
) -> list[ProductDTO]:
    return service.get_related(product_id, limit)
