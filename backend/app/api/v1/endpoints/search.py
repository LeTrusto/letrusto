from fastapi import APIRouter, Depends, Query

from app.api.deps import get_product_service
from app.schemas.product import PaginatedProductsResponse, ProductSearchQuery
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["search"])


@router.get("/search", response_model=PaginatedProductsResponse)
def search_products(
    q: str = "",
    sort: str = Query(default="relevance"),
    category: str = Query(default="all"),
    subcategory: str | None = None,
    series: str | None = None,
    price: str = Query(default="all"),
    rating: str = Query(default="all"),
    aiScore: str = Query(default="all"),
    brand: str | None = None,
    minPrice: int | None = Query(default=None, ge=0),
    maxPrice: int | None = Query(default=None, ge=0),
    minRating: float | None = Query(default=None, ge=0, le=5),
    minAiScore: int | None = Query(default=None, ge=0, le=100),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=12, ge=1, le=100),
    service: ProductService = Depends(get_product_service),
) -> PaginatedProductsResponse:
    query = ProductSearchQuery(
        q=q,
        sort=sort,
        category=category,
        subcategory=subcategory,
        series=series,
        price=price,
        rating=rating,
        aiScore=aiScore,
        brand=brand,
        minPrice=minPrice,
        maxPrice=maxPrice,
        minRating=minRating,
        minAiScore=minAiScore,
        page=page,
        pageSize=pageSize,
    )
    return service.get_search(query)
