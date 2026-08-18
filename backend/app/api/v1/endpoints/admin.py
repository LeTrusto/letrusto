from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_admin_product_service, get_admin_service, get_current_admin, get_fulfillment_service
from app.models.entities import User
from app.schemas.admin import AdminDashboardStats, AdminUserListResponse
from app.schemas.admin_products import (
    AdminProductDTO,
    AdminProductListResponse,
    BulkApprovedProductImportRequest,
    BulkApprovedProductImportResponse,
    CommercialReviewResponse,
    MarketEvidenceCreate,
    MarketEvidenceDTO,
    MarketEvidenceResponse,
    PriceCalculationRequest,
    PriceCalculationResponse,
    ProductImportRequest,
    ProductRejectionRequest,
    ProductStatusUpdate,
    SupplierCandidateCreate,
    SupplierCandidateDTO,
    SupplierCandidateListResponse,
    SupplierCandidateRejectionRequest,
    VariantPriceCalculationResponse,
)
from app.services.admin_service import AdminService
from app.services.admin_product_service import AdminProductService
from app.services.fulfillment_service import FulfillmentService
from app.schemas.payments import AdminFulfillmentOrderDTO, FulfillmentDTO

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/orders/fulfillment", response_model=list[AdminFulfillmentOrderDTO])
def list_fulfillment_orders(
    _: User = Depends(get_current_admin),
    service: FulfillmentService = Depends(get_fulfillment_service),
):
    return service.list_orders()


@router.post("/orders/{order_id}/fulfillment", response_model=FulfillmentDTO)
async def submit_order_fulfillment(
    order_id: UUID,
    _: User = Depends(get_current_admin),
    service: FulfillmentService = Depends(get_fulfillment_service),
):
    order = await service.submit(order_id)
    return FulfillmentDTO(order_id=order.id, fulfillment_status=order.fulfillment_status, supplier_order_id=order.supplier_order_id, failure_reason=order.fulfillment_failure_reason)


@router.post("/orders/{order_id}/sync-fulfillment", response_model=FulfillmentDTO)
async def sync_order_fulfillment(
    order_id: UUID,
    _: User = Depends(get_current_admin),
    service: FulfillmentService = Depends(get_fulfillment_service),
):
    order = await service.sync_tracking(order_id)
    return FulfillmentDTO(order_id=order.id, fulfillment_status=order.fulfillment_status, supplier_order_id=order.supplier_order_id, failure_reason=order.fulfillment_failure_reason)


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


@router.post("/products/bulk-import", response_model=BulkApprovedProductImportResponse)
async def bulk_import_approved_products(
    payload: BulkApprovedProductImportRequest,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> BulkApprovedProductImportResponse:
    return await service.bulk_import_approved(payload)


@router.post("/supplier-candidates", response_model=SupplierCandidateDTO)
async def create_supplier_candidate(
    payload: SupplierCandidateCreate,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> SupplierCandidateDTO:
    return await service.create_supplier_candidate(payload)


@router.get("/supplier-candidates", response_model=SupplierCandidateListResponse)
def list_supplier_candidates(
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> SupplierCandidateListResponse:
    return service.list_supplier_candidates()


@router.get("/supplier-candidates/{candidate_id}", response_model=SupplierCandidateDTO)
def get_supplier_candidate(
    candidate_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> SupplierCandidateDTO:
    return service.get_supplier_candidate(candidate_id)


@router.post("/supplier-candidates/{candidate_id}/market-evidence", response_model=MarketEvidenceDTO)
def create_supplier_candidate_market_evidence(
    candidate_id: UUID,
    payload: MarketEvidenceCreate,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> MarketEvidenceDTO:
    return service.create_candidate_market_evidence(candidate_id, payload)


@router.get("/supplier-candidates/{candidate_id}/market-evidence", response_model=MarketEvidenceResponse)
def get_supplier_candidate_market_evidence(
    candidate_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> MarketEvidenceResponse:
    return service.get_candidate_market_evidence(candidate_id)


@router.delete(
    "/supplier-candidates/{candidate_id}/market-evidence/{evidence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_supplier_candidate_market_evidence(
    candidate_id: UUID,
    evidence_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> Response:
    service.delete_candidate_market_evidence(candidate_id, evidence_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/supplier-candidates/{candidate_id}/approve", response_model=SupplierCandidateDTO)
def approve_supplier_candidate(
    candidate_id: UUID,
    current_admin: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> SupplierCandidateDTO:
    return service.approve_supplier_candidate(candidate_id, current_admin)


@router.post("/supplier-candidates/{candidate_id}/reject", response_model=SupplierCandidateDTO)
def reject_supplier_candidate(
    candidate_id: UUID,
    payload: SupplierCandidateRejectionRequest,
    current_admin: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> SupplierCandidateDTO:
    return service.reject_supplier_candidate(candidate_id, payload.reason, current_admin)


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
