from fastapi import APIRouter, Depends

from app.api.deps import get_product_service
from app.schemas.category import CatalogTreeResponse, CategoriesResponse, CategoryDTO, CategoryTreeNode
from app.services.product_service import ProductService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=CategoriesResponse)
def list_categories(service: ProductService = Depends(get_product_service)) -> CategoriesResponse:
    categories = service.repository.get_categories()
    return CategoriesResponse(items=[
        CategoryDTO(
            id=item.id,
            name=item.name,
            slug=item.slug,
            parent_slug=item.parent.slug if item.parent else None,
            icon=item.icon,
            position=item.position,
        )
        for item in categories
    ])


@router.get("/tree", response_model=CatalogTreeResponse)
def get_catalog_tree(service: ProductService = Depends(get_product_service)) -> CatalogTreeResponse:
    top_level = service.repository.get_top_level_categories()

    def _to_node(cat) -> CategoryTreeNode:
        return CategoryTreeNode(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            icon=cat.icon,
            position=cat.position,
            children=sorted(
                [_to_node(c) for c in cat.children],
                key=lambda n: n.position,
            ),
        )

    return CatalogTreeResponse(tree=[_to_node(cat) for cat in top_level])
