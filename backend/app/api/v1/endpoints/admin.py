from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_admin_product_service, get_admin_service, get_current_admin, get_fulfillment_service, get_db
from app.core.config import get_settings
from app.core.trust import TRUST_CLAIM_STATUSES, TRUST_VERIFICATION_METHODS
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
    SupplierCandidateDiscoveryRequest,
    SupplierCandidateDiscoveryResponse,
    SupplierCandidateDTO,
    SupplierCandidateListResponse,
    SupplierCandidateReadinessTransitionRequest,
    SupplierCandidateRejectionRequest,
    VariantPriceCalculationResponse,
)
from app.services.admin_service import AdminService
from app.services.admin_product_service import AdminProductService
from app.services.fulfillment_service import FulfillmentService
from app.services.inventory_reservation_service import InventoryReservationService
from app.services.order_reconciliation_service import OrderLifecycleReconciliationService
from app.schemas.reconciliation import ReconciliationResultDTO
from app.schemas.reservations import AdminInventoryReservationDTO
from app.schemas.payments import AdminFulfillmentOrderDTO, AdminSupplierPaymentDTO, FulfillmentDTO, SupplierPaymentRequest
from app.schemas.admin_analytics import AnalyticsPeriod, AnalyticsSummary, InventoryAnalyticsDTO, OrderProfitabilityDTO, ProductPerformanceDTO, SalesTrendPoint, VariantPerformanceDTO
from app.services.admin_analytics_service import AdminAnalyticsService
from app.schemas.marketing import AttributionCreate, AttributionDTO, MarketingCACResponse, MarketingSpendCreate, MarketingSpendDTO
from app.services.marketing_service import MarketingService
from app.schemas.trust import (
    TrustAuditEventDTO,
    TrustClaimCreate,
    TrustClaimDetailDTO,
    TrustClaimEvidenceCreate,
    TrustClaimEvidenceDTO,
    TrustClaimDTO,
    TrustClaimUpdate,
    TrustEvidenceCreate,
    TrustEvidenceDTO,
    TrustEvidenceUpdate,
    TrustVerificationCreate,
    TrustVerificationDTO,
)
from app.services.trust_service import TrustService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/trust/options")
def trust_options(_: User = Depends(get_current_admin)):
    return {"claim_statuses": TRUST_CLAIM_STATUSES, "verification_methods": TRUST_VERIFICATION_METHODS}


@router.post("/trust/claims", response_model=TrustClaimDTO, status_code=201)
def create_trust_claim(payload: TrustClaimCreate, admin: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).create_claim(payload, admin)


@router.get("/trust/products/{product_id}/claims", response_model=list[TrustClaimDTO])
def list_product_trust_claims(product_id: UUID, _: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).list_product_claims(product_id)


@router.get("/trust/claims/{claim_id}", response_model=TrustClaimDetailDTO)
def get_trust_claim(claim_id: UUID, _: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).get_claim(claim_id)


@router.patch("/trust/claims/{claim_id}", response_model=TrustClaimDTO)
def update_trust_claim(claim_id: UUID, payload: TrustClaimUpdate, admin: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).update_claim(claim_id, payload, admin)


@router.post("/trust/evidence", response_model=TrustEvidenceDTO, status_code=201)
def create_trust_evidence(payload: TrustEvidenceCreate, admin: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).create_evidence(payload, admin)


@router.get("/trust/evidence/{evidence_id}", response_model=TrustEvidenceDTO)
def get_trust_evidence(evidence_id: UUID, _: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).get_evidence(evidence_id)


@router.patch("/trust/evidence/{evidence_id}", response_model=TrustEvidenceDTO)
def update_trust_evidence(evidence_id: UUID, payload: TrustEvidenceUpdate, admin: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).update_evidence(evidence_id, payload, admin)


@router.post("/trust/claims/{claim_id}/evidence", response_model=TrustClaimEvidenceDTO, status_code=201)
def attach_trust_evidence(claim_id: UUID, payload: TrustClaimEvidenceCreate, admin: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).attach_evidence(claim_id, payload, admin)


@router.post("/trust/claims/{claim_id}/verifications", response_model=TrustVerificationDTO, status_code=201)
def create_trust_verification(claim_id: UUID, payload: TrustVerificationCreate, admin: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).create_verification(claim_id, payload, admin)


@router.get("/trust/claims/{claim_id}/verifications", response_model=list[TrustVerificationDTO])
def list_trust_verifications(claim_id: UUID, _: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).verification_history(claim_id)


@router.get("/trust/claims/{claim_id}/audit", response_model=list[TrustAuditEventDTO])
def list_trust_audit(claim_id: UUID, _: User = Depends(get_current_admin), db=Depends(get_db)):
    return TrustService(db).audit_history(claim_id)

@router.post("/marketing/spend", response_model=MarketingSpendDTO, status_code=201)
def create_marketing_spend(payload: MarketingSpendCreate, _: User = Depends(get_current_admin), db=Depends(get_db)):
    return MarketingService(db).create_spend(payload)

@router.get("/marketing/spend", response_model=list[MarketingSpendDTO])
def list_marketing_spend(period: str = Query(default="last_30_days"), _: User = Depends(get_current_admin), db=Depends(get_db)):
    start, end = MarketingService.periods(period)
    return MarketingService(db).list_spend(start, end)

@router.get("/marketing/spend/{spend_id}", response_model=MarketingSpendDTO)
def get_marketing_spend(spend_id: UUID, _: User = Depends(get_current_admin), db=Depends(get_db)):
    return MarketingService(db).get_spend(spend_id)

@router.put("/marketing/spend/{spend_id}", response_model=MarketingSpendDTO)
def update_marketing_spend(spend_id: UUID, payload: MarketingSpendCreate, _: User = Depends(get_current_admin), db=Depends(get_db)):
    return MarketingService(db).update_spend(spend_id, payload)

@router.delete("/marketing/spend/{spend_id}", status_code=204)
def delete_marketing_spend(spend_id: UUID, _: User = Depends(get_current_admin), db=Depends(get_db)):
    MarketingService(db).delete_spend(spend_id)

@router.post("/marketing/attribution", response_model=AttributionDTO, status_code=201)
def create_marketing_attribution(payload: AttributionCreate, _: User = Depends(get_current_admin), db=Depends(get_db)):
    return MarketingService(db).attribute(payload)

@router.get("/marketing/cac", response_model=MarketingCACResponse)
def marketing_cac(period: str = Query(default="last_30_days"), _: User = Depends(get_current_admin), db=Depends(get_db)):
    start, end = MarketingService.periods(period)
    return MarketingService(db).cac(start, end)

@router.get("/marketing/campaigns", response_model=MarketingCACResponse)
def marketing_campaigns(period: str = Query(default="last_30_days"), _: User = Depends(get_current_admin), db=Depends(get_db)):
    start, end = MarketingService.periods(period)
    return MarketingService(db).cac(start, end)


def _analytics_period(period: str, start_date: date | None, end_date: date | None) -> AnalyticsPeriod:
    try:
        return AdminAnalyticsService.resolve_period(period, start_date, end_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary(
    period: str = Query(default="last_30_days"), start_date: date | None = None, end_date: date | None = None,
    _: User = Depends(get_current_admin), db=Depends(get_db),
) -> AnalyticsSummary:
    return AdminAnalyticsService(db).summary(_analytics_period(period, start_date, end_date))


@router.get("/analytics/products", response_model=list[ProductPerformanceDTO])
def analytics_products(
    period: str = Query(default="last_30_days"), start_date: date | None = None, end_date: date | None = None,
    _: User = Depends(get_current_admin), db=Depends(get_db),
) -> list[ProductPerformanceDTO]:
    return AdminAnalyticsService(db).product_performance(_analytics_period(period, start_date, end_date))


@router.get("/analytics/variants", response_model=list[VariantPerformanceDTO])
def analytics_variants(
    period: str = Query(default="last_30_days"), start_date: date | None = None, end_date: date | None = None,
    _: User = Depends(get_current_admin), db=Depends(get_db),
) -> list[VariantPerformanceDTO]:
    return AdminAnalyticsService(db).variant_performance(_analytics_period(period, start_date, end_date))


@router.get("/analytics/inventory", response_model=list[InventoryAnalyticsDTO])
def analytics_inventory(_: User = Depends(get_current_admin), db=Depends(get_db)) -> list[InventoryAnalyticsDTO]:
    return AdminAnalyticsService(db).inventory()


@router.get("/analytics/orders/{order_id}/profitability", response_model=OrderProfitabilityDTO)
def analytics_order_profitability(
    order_id: UUID,
    _: User = Depends(get_current_admin), db=Depends(get_db),
) -> OrderProfitabilityDTO:
    try:
        return AdminAnalyticsService(db).order_profitability(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/analytics/sales-trend", response_model=list[SalesTrendPoint])
def analytics_sales_trend(
    period: str = Query(default="last_30_days"), start_date: date | None = None, end_date: date | None = None,
    _: User = Depends(get_current_admin), db=Depends(get_db),
) -> list[SalesTrendPoint]:
    return AdminAnalyticsService(db).sales_trend(_analytics_period(period, start_date, end_date))


@router.get("/analytics/export")
def analytics_export(
    period: str = Query(default="last_30_days"), start_date: date | None = None, end_date: date | None = None,
    _: User = Depends(get_current_admin), db=Depends(get_db),
) -> StreamingResponse:
    content = AdminAnalyticsService(db).export_csv(_analytics_period(period, start_date, end_date))
    return StreamingResponse(iter([content]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=letrusto-analytics.csv"})


@router.post("/reconciliation/run", response_model=ReconciliationResultDTO)
async def run_reconciliation(
    _: User = Depends(get_current_admin),
    db=Depends(get_db),
) -> ReconciliationResultDTO:
    if not get_settings().ORDER_RECONCILIATION_ENABLED:
        raise HTTPException(status_code=503, detail="Order reconciliation is disabled")
    return await OrderLifecycleReconciliationService(db).run_order_lifecycle_reconciliation()


@router.get("/inventory-reservations", response_model=list[AdminInventoryReservationDTO])
def list_inventory_reservations(
    order_id: UUID | None = Query(default=None),
    _: User = Depends(get_current_admin),
    db=Depends(get_db),
) -> list[AdminInventoryReservationDTO]:
    service = InventoryReservationService(db)
    service.release_expired()
    return [
        AdminInventoryReservationDTO(
            id=row.id,
            order_number=row.order.order_number,
            product_name=row.order_item.product_name,
            variant_name=row.order_item.variant_name,
            variant_id=row.variant_id,
            quantity=row.quantity,
            status=row.status,
            created_at=row.created_at.isoformat(),
            expires_at=row.expires_at.isoformat(),
            released_at=row.released_at.isoformat() if row.released_at else None,
            consumed_at=row.consumed_at.isoformat() if row.consumed_at else None,
        )
        for row in service.list_for_admin(order_id)
    ]


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


@router.post("/orders/{order_id}/supplier-payment", response_model=AdminSupplierPaymentDTO)
async def pay_supplier_order(
    order_id: UUID,
    payload: SupplierPaymentRequest,
    _: User = Depends(get_current_admin),
    service: FulfillmentService = Depends(get_fulfillment_service),
) -> AdminSupplierPaymentDTO:
    order = await service.pay_supplier(order_id, float(payload.required_amount_usd))
    if not order.supplier_order_id or not order.supplier_shipment_order_id:
        raise HTTPException(status_code=409, detail="Supplier payment record is incomplete")
    return AdminSupplierPaymentDTO(
        order_id=order.id,
        supplier_order_id=order.supplier_order_id,
        supplier_shipment_order_id=order.supplier_shipment_order_id,
        required_amount_usd=payload.required_amount_usd,
        payment_state=order.supplier_payment_state or "UNKNOWN",
        supplier_status=order.supplier_status,
        payment_error=order.supplier_payment_error,
        confirmation_required=order.supplier_payment_state != "PAID",
    )


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


@router.post("/supplier-candidates/discover", response_model=SupplierCandidateDiscoveryResponse)
async def discover_supplier_candidates(
    payload: SupplierCandidateDiscoveryRequest,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> SupplierCandidateDiscoveryResponse:
    return await service.discover_supplier_candidates(payload)


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


@router.post(
    "/supplier-candidates/{candidate_id}/readiness",
    response_model=SupplierCandidateDTO,
)
def transition_supplier_candidate_readiness(
    candidate_id: UUID,
    payload: SupplierCandidateReadinessTransitionRequest,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> SupplierCandidateDTO:
    return service.transition_supplier_candidate_readiness(candidate_id, payload.target)


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


@router.post("/products/{product_id}/revalidate-supplier", response_model=AdminProductDTO)
async def revalidate_catalog_product_supplier(
    product_id: UUID,
    _: User = Depends(get_current_admin),
    service: AdminProductService = Depends(get_admin_product_service),
) -> AdminProductDTO:
    return await service.revalidate_supplier(product_id)


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
