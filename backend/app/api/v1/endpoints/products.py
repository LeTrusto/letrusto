from fastapi import APIRouter, Depends, Query

from app.api.deps import get_product_service
from app.schemas.product import CatalogMetadataResponse, HomeCollectionsResponse, ProductDTO
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductDTO])
def list_products(
    ids: str | None = Query(default=None, description="Comma-separated product ids/slugs"),
    service: ProductService = Depends(get_product_service),
) -> list[ProductDTO]:
    parsed_ids = [value.strip() for value in ids.split(",") if value.strip()] if ids else None
    return service.list_products(parsed_ids)


@router.get("/metadata", response_model=CatalogMetadataResponse)
def get_metadata(service: ProductService = Depends(get_product_service)) -> CatalogMetadataResponse:
    import traceback
    try:
        return service.get_metadata()
    except Exception:
        traceback.print_exc()
        raise


@router.get("/collections/home", response_model=HomeCollectionsResponse)
def get_home_collections(service: ProductService = Depends(get_product_service)) -> HomeCollectionsResponse:
    import traceback
    try:
        return service.get_home_collections()
    except Exception:
        traceback.print_exc()
        raise


@router.get("/suggestions", response_model=list[str])
def get_suggestions(
    limit: int = Query(default=24, ge=1, le=100),
    service: ProductService = Depends(get_product_service),
) -> list[str]:
    return service.get_suggestions(limit)


@router.get("/{product_id}", response_model=ProductDTO)
def get_product(product_id: str, service: ProductService = Depends(get_product_service)) -> ProductDTO:
    return service.get_product(product_id)
