from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_admin_product_service, get_admin_service, get_current_admin
from app.models.entities import User
from app.schemas.admin import AdminDashboardStats, AdminUserListResponse
from app.schemas.admin_products import (
    AdminProductDTO,
    AdminProductListResponse,
    CommercialReviewResponse,
    MarketEvidenceCreate,
    MarketEvidenceDTO,
    MarketEvidenceResponse,
    PriceCalculationRequest,
    PriceCalculationResponse,
    ProductImportRequest,
    ProductRejectionRequest,
    ProductStatusUpdate,
    VariantPriceCalculationResponse,
)
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
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductListResponse:
    return service.list_products(status=status, supplier=supplier, skip=skip, limit=limit)


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


@router.post("/products/{product_id}/calculate-price", response_model=PriceCalculationResponse)
def calculate_catalog_product_price(
    product_id: UUID,
    payload: PriceCalculationRequest,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> PriceCalculationResponse:
    return service.calculate_price(product_id, payload)


@router.post(
    "/products/{product_id}/calculate-variant-prices",
    response_model=VariantPriceCalculationResponse,
)
def calculate_catalog_product_variant_prices(
    product_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> VariantPriceCalculationResponse:
    return service.calculate_variant_prices(product_id)


@router.post(
    "/products/{product_id}/commercial-review",
    response_model=CommercialReviewResponse,
)
def review_catalog_product_commercially(
    product_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> CommercialReviewResponse:
    return service.commercial_review(product_id)


@router.post("/products/{product_id}/approve", response_model=AdminProductDTO)
def approve_catalog_product(
    product_id: UUID,
    current_admin: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductDTO:
    return service.approve(product_id, current_admin)


@router.post("/products/{product_id}/reject", response_model=AdminProductDTO)
def reject_catalog_product(
    product_id: UUID,
    payload: ProductRejectionRequest | None = None,
    current_admin: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductDTO:
    return service.reject(product_id, payload or ProductRejectionRequest(), current_admin)


@router.post("/products/{product_id}/activate", response_model=AdminProductDTO)
def activate_catalog_product(
    product_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductDTO:
    return service.activate(product_id)


@router.post("/products/{product_id}/pause", response_model=AdminProductDTO)
def pause_catalog_product(
    product_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductDTO:
    return service.pause(product_id)


@router.post("/products/{product_id}/sync-inventory", response_model=AdminProductDTO)
async def sync_catalog_product_inventory(
    product_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductDTO:
    return await service.sync_inventory(product_id)


@router.post("/products/{product_id}/market-evidence", response_model=MarketEvidenceDTO)
def create_catalog_product_market_evidence(
    product_id: UUID,
    payload: MarketEvidenceCreate,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> MarketEvidenceDTO:
    return service.create_market_evidence(product_id, payload)


@router.get("/products/{product_id}/market-evidence", response_model=MarketEvidenceResponse)
def get_catalog_product_market_evidence(
    product_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> MarketEvidenceResponse:
    return service.get_market_evidence(product_id)


@router.delete(
    "/products/{product_id}/market-evidence/{evidence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_catalog_product_market_evidence(
    product_id: UUID,
    evidence_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> Response:
    service.delete_market_evidence(product_id, evidence_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
