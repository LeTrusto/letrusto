from fastapi import APIRouter, Depends

from app.api.deps import get_product_service
from app.schemas.category import CategoriesResponse, CategoryDTO
from app.services.product_service import ProductService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=CategoriesResponse)
def list_categories(service: ProductService = Depends(get_product_service)) -> CategoriesResponse:
    categories = service.repository.get_categories()
    return CategoriesResponse(items=[CategoryDTO(id=item.id, name=item.name, slug=item.slug) for item in categories])
