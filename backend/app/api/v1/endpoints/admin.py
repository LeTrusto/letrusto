from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_admin_product_service, get_admin_service, get_current_admin
from app.models.entities import User
from app.schemas.admin import AdminDashboardStats, AdminUserListResponse
from app.schemas.admin_products import AdminProductDTO, AdminProductListResponse, ProductImportRequest, ProductStatusUpdate
from app.services.admin_service import AdminService
from app.services.admin_product_service import AdminProductService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminDashboardStats)
def get_stats(
    _: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
) -> AdminDashboardStats:
    return service.get_dashboard_stats()


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
) -> AdminUserListResponse:
    return service.list_users(skip=skip, limit=limit)


@router.post("/products/import", response_model=AdminProductDTO)
async def import_product(
    payload: ProductImportRequest,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductDTO:
    return await service.import_product(payload)


@router.get("/products", response_model=AdminProductListResponse)
def list_catalog_products(
    status: str | None = Query(default=None),
    supplier: str | None = Query(default=None),
    include_legacy: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductListResponse:
    return service.list_products(status=status, supplier=supplier, include_legacy=include_legacy, skip=skip, limit=limit)


@router.get("/products/{product_id}", response_model=AdminProductDTO)
def get_catalog_product(
    product_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductDTO:
    return service.get_product(product_id)


@router.patch("/products/{product_id}", response_model=AdminProductDTO)
def update_catalog_product(
    product_id: UUID,
    payload: ProductStatusUpdate,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductDTO:
    return service.update_status(product_id, payload)
