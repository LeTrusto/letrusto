from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID, uuid4

import httpx
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload, sessionmaker

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.catalog_readiness import resolve_cj_category
from app.models.entities import Brand, Category
from app.services.catalog_readiness_service import CatalogReadinessService
from app.models.entities import (
    Product,
    ProductImage,
    ProductMarketEvidence,
    ProductVariant,
    SupplierCandidate,
    SupplierVariantInventory,
    User,
)
from app.schemas.admin_products import (
    AdminProductDTO,
    AdminProductListResponse,
    AdminProductVariantDTO,
    BulkApprovedProductImportItem,
    BulkApprovedProductImportRequest,
    BulkApprovedProductImportResponse,
    CommercialReviewResponse,
    MarketEvidenceAnalysis,
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
    VariantPriceCalculation,
    VariantPriceCalculationResponse,
)
from app.services.commercial_review_service import evaluate_commercial_product
from app.services.launch_pricing_policy import LaunchPricingPolicy, load_launch_pricing_policy
from app.services.pricing_engine import calculate_launch_variant_price, calculate_margin_price
from app.suppliers.economics import EconomicsConfig, calculate_economics
from app.suppliers.factory import build_supplier_adapter
from app.suppliers.normalizer import normalize_product
from app.suppliers.scoring import score_product


class AdminProductService:
    def __init__(self, db: Session, launch_pricing_policy: LaunchPricingPolicy | None = None) -> None:
        self.db = db
        self.launch_pricing_policy = launch_pricing_policy or load_launch_pricing_policy()

    def list_products(self, status: str | None, supplier: str | None, skip: int, limit: int) -> AdminProductListResponse:
        stmt = select(Product).options(selectinload(Product.images), selectinload(Product.variants)).order_by(Product.created_at.desc())
        count_stmt = select(func.count(Product.id))
        if supplier:
            stmt = stmt.where(Product.supplier == supplier)
            count_stmt = count_stmt.where(Product.supplier == supplier)
        else:
            stmt = stmt.where(Product.supplier.is_not(None))
            count_stmt = count_stmt.where(Product.supplier.is_not(None))
        if status:
            stmt = stmt.where(Product.status == status)
            count_stmt = count_stmt.where(Product.status == status)
        products = list(self.db.scalars(stmt.offset(skip).limit(limit)).unique().all())
        return AdminProductListResponse(products=[self._dto(p) for p in products], total=self.db.scalar(count_stmt) or 0)

    def get_product(self, product_id: UUID) -> AdminProductDTO:
        return self._dto(self._get(product_id))

    async def import_product(self, payload: ProductImportRequest, *, commit: bool = True) -> AdminProductDTO:
        existing = self.db.scalar(select(Product).where(Product.supplier == payload.supplier, Product.supplier_product_id == payload.supplier_product_id))
        if existing:
            return self._dto(self._get(existing.id))

        adapter = build_supplier_adapter(payload.supplier)
        if not await adapter.authenticate():
            raise BadRequestError("Supplier authentication failed")
        raw = await adapter.get_product(payload.supplier_product_id)
        if not raw:
            raise NotFoundError("Supplier product not found")

        config = EconomicsConfig()
        normalized = normalize_product(raw, usd_to_inr=config.usd_to_inr)
        shipping = None
        if normalized.variants:
            shipping = await adapter.calculate_shipping(normalized.variants[0].supplier_variant_id, payload.destination, origin_country=normalized.warehouse_country or "CN")
        shipping_usd = shipping.options[0].cost_usd if shipping and shipping.options else None
        economics = calculate_economics(normalized, shipping_cost_usd=shipping_usd, config=config)
        product_score = score_product(normalized, economics=economics, shipping=shipping)
        validated_at = datetime.now(timezone.utc)
        category_resolution = resolve_cj_category(
            normalized.supplier_category_id,
            normalized.category,
            normalized.supplier_product_id,
        )
        category = None
        if category_resolution.category_slug:
            category = self.db.scalar(select(Category).where(Category.slug == category_resolution.category_slug))

        product = Product(
            id=uuid4(), slug=self._unique_slug(normalized.title, normalized.supplier_product_id), name=normalized.title,
            description=normalized.description or normalized.title, status="DRAFT", supplier=normalized.supplier_id,
            supplier_product_id=normalized.supplier_product_id,
            category_id=category.id if category else None,
            supplier_cost=Decimal(str(raw.price_usd * config.usd_to_inr)) if raw.price_usd is not None else None,
            shipping_cost=Decimal(str(economics.shipping_cost_inr.amount_inr)) if economics.shipping_cost_inr.amount_inr is not None else None,
            selling_price=Decimal(str(economics.selling_price_inr)) if economics.selling_price_inr is not None else None,
            currency="INR", total_inventory=raw.total_inventory, cj_inventory=normalized.total_inventory,
            factory_inventory=normalized.factory_inventory, verified_warehouse=normalized.inventory_verification,
            last_supplier_sync_at=datetime.now(timezone.utc),
            supplier_validation_status=product_score.verdict.value,
            supplier_validation_score=product_score.score,
            supplier_validation_notes=product_score.notes,
            supplier_validated_at=validated_at,
            supplier_validation_details={
                "calculation_origin": "IMPORT",
                "historical_evidence_available": True,
                "breakdown": {
                    "supplier_reliability": product_score.breakdown.supplier_reliability,
                    "shipping_feasibility": product_score.breakdown.shipping_feasibility,
                    "margin_score": product_score.breakdown.margin_score,
                    "inventory_score": product_score.breakdown.inventory_score,
                    "data_completeness": product_score.breakdown.data_completeness,
                    "return_risk": product_score.breakdown.return_risk,
                },
                "missing_fields": normalized.missing_fields,
                "unknown_costs": economics.unknown_costs,
                "variants": [
                    {
                        "supplier_variant_id": variant.supplier_variant_id,
                        "supplier_variant_sku": variant.supplier_variant_sku,
                        "cost_usd": variant.cost_usd,
                        "weight_grams": variant.weight_grams,
                        "total_inventory": variant.total_inventory,
                        "cj_inventory": variant.cj_inventory,
                        "factory_inventory": variant.factory_inventory,
                    }
                    for variant in normalized.variants
                ],
            },
        )
        self.db.add(product)
        self.db.flush()
        for position, image_url in enumerate(normalized.images, start=1):
            self.db.add(ProductImage(product_id=product.id, url=image_url, position=position))
        for position, variant in enumerate(normalized.variants, start=1):
            self.db.add(ProductVariant(
                product_id=product.id, supplier_variant_id=variant.supplier_variant_id,
                supplier_variant_sku=variant.supplier_variant_sku, name=variant.name,
                attributes=variant.option_key, supplier_cost=Decimal(str(variant.cost_inr)) if variant.cost_inr is not None else None,
                supplier_cost_usd=Decimal(str(variant.cost_usd)) if variant.cost_usd is not None else None,
                total_inventory=variant.total_inventory, cj_inventory=variant.cj_inventory,
                factory_inventory=variant.factory_inventory, verified_warehouse=variant.inventory_verification,
                weight_grams=Decimal(str(variant.weight_grams)) if variant.weight_grams is not None else None, position=position,
            ))
        if commit:
            self.db.commit()
        else:
            self.db.flush()
        return self._dto(self._get(product.id))

    async def create_supplier_candidate(
        self, payload: SupplierCandidateCreate
    ) -> SupplierCandidateDTO:
        adapter = build_supplier_adapter(payload.supplier)
        if not await adapter.authenticate():
            raise BadRequestError("Supplier authentication failed")
        raw = await adapter.get_product(payload.supplier_product_id)
        if not raw:
            raise NotFoundError("Supplier product not found")

        config = EconomicsConfig()
        normalized = normalize_product(raw, usd_to_inr=config.usd_to_inr, derive_variant_fields=True)
        shipping = None
        shipping_identifier = (
            normalized.variants[0].supplier_variant_id
            if normalized.variants
            else raw.supplier_product_id
        )
        if shipping_identifier:
            shipping = await adapter.calculate_shipping(
                shipping_identifier,
                payload.destination,
                origin_country=normalized.warehouse_country or "CN",
            )
        shipping_usd = shipping.options[0].cost_usd if shipping and shipping.options else None
        economics = calculate_economics(normalized, shipping_cost_usd=shipping_usd, config=config)
        product_score = score_product(normalized, economics=economics, shipping=shipping)
        shipping_cost_inr = Decimal(str(shipping_usd * config.usd_to_inr)) if shipping_usd is not None else Decimal("0")
        variant_snapshot = []
        for variant in normalized.variants:
            price = None
            if variant.cost_usd is not None:
                price = calculate_launch_variant_price(
                    supplier_cost_usd=Decimal(str(variant.cost_usd)),
                    shipping_cost_inr=shipping_cost_inr,
                    policy=self.launch_pricing_policy,
                )
            variant_snapshot.append({
                "supplier_variant_id": variant.supplier_variant_id,
                "supplier_variant_sku": variant.supplier_variant_sku,
                "name": variant.name,
                "attributes": variant.option_key,
                "supplier_cost_usd": variant.cost_usd,
                "supplier_cost_inr": variant.cost_inr,
                "weight_grams": variant.weight_grams,
                "total_inventory": variant.total_inventory,
                "cj_inventory": variant.cj_inventory,
                "factory_inventory": variant.factory_inventory,
                "selling_price_inr": str(price.selling_price_inr) if price else None,
                "target_margin_status": price.target_margin_status if price else None,
                "cac_target_status": price.cac_target_status if price else None,
            })
        selling_prices = [Decimal(item["selling_price_inr"]) for item in variant_snapshot if item["selling_price_inr"]]

        existing = self.db.scalar(
            select(SupplierCandidate).where(
                SupplierCandidate.supplier == raw.supplier_id,
                SupplierCandidate.supplier_product_id == raw.supplier_product_id,
            )
        )
        if existing:
            return self._candidate_dto(existing)

        candidate = SupplierCandidate(
            supplier=raw.supplier_id,
            supplier_product_id=raw.supplier_product_id,
            supplier_sku=raw.supplier_sku or None,
            name=raw.title,
            approval_status="REVIEW",
            supplier_validation_status=product_score.verdict.value,
            supplier_validation_score=product_score.score,
            commercial_status="REVIEW",
            market_status="NOT_EVALUATED",
            discovery_min_selling_price_inr=min(selling_prices) if selling_prices else None,
            discovery_max_selling_price_inr=max(selling_prices) if selling_prices else None,
            snapshot_status="AVAILABLE",
            data_snapshot={
                "main_image": normalized.images[0] if normalized.images else None,
                "images": normalized.images,
                "validation_issues": product_score.notes,
                "target_margin_percent": str(self.launch_pricing_policy.target_contribution_margin_pct),
                "target_cac_inr": str(self.launch_pricing_policy.target_cac_inr),
                "cac_viable": all(item["cac_target_status"] == "CAC_TARGET_SUPPORTED" for item in variant_snapshot if item["cac_target_status"]),
                "variants": variant_snapshot,
            },
        )
        self.db.add(candidate)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing = self.db.scalar(
                select(SupplierCandidate).where(
                    SupplierCandidate.supplier == raw.supplier_id,
                    SupplierCandidate.supplier_product_id == raw.supplier_product_id,
                )
            )
            if existing:
                return self._candidate_dto(existing)
            raise
        self.db.refresh(candidate)
        return self._candidate_dto(candidate)

    def list_supplier_candidates(self) -> SupplierCandidateListResponse:
        candidates = list(
            self.db.scalars(
                select(SupplierCandidate).order_by(
                    SupplierCandidate.created_at.desc(), SupplierCandidate.id.desc()
                )
            )
        )
        return SupplierCandidateListResponse(
            candidates=[self._candidate_dto(candidate) for candidate in candidates],
            total=len(candidates),
        )

    def approve_supplier_candidate(
        self, candidate_id: UUID, current_admin: User
    ) -> SupplierCandidateDTO:
        candidate = self._get_candidate(candidate_id)
        if candidate.approval_status == "IMPORTED":
            raise BadRequestError("Imported supplier candidate cannot be approved again")
        if candidate.supplier_validation_status == "REJECT":
            raise BadRequestError("Supplier candidate rejected by supplier validation cannot be approved")
        if candidate.approval_status != "APPROVED":
            candidate.approval_status = "APPROVED"
            candidate.commercial_status = "APPROVED"
            candidate.approved_at = datetime.now(timezone.utc)
            candidate.approved_by_user_id = current_admin.id
            candidate.decision_at = candidate.approved_at
            candidate.decision_by_user_id = current_admin.id
            candidate.rejection_reason = None
            self.db.commit()
            self.db.refresh(candidate)
        return self._candidate_dto(candidate)

    def reject_supplier_candidate(
        self, candidate_id: UUID, reason: str | None = None, current_admin: User | None = None
    ) -> SupplierCandidateDTO:
        candidate = self._get_candidate(candidate_id)
        if candidate.approval_status == "IMPORTED":
            raise BadRequestError("Imported supplier candidate cannot be rejected")
        candidate.approval_status = "REJECTED"
        candidate.commercial_status = "REJECTED"
        candidate.approved_at = None
        candidate.approved_by_user_id = None
        candidate.decision_at = datetime.now(timezone.utc)
        candidate.decision_by_user_id = current_admin.id if current_admin else None
        candidate.rejection_reason = reason or "Admin rejected candidate"
        self.db.commit()
        self.db.refresh(candidate)
        return self._candidate_dto(candidate)

    async def bulk_import_approved(
        self, payload: BulkApprovedProductImportRequest
    ) -> BulkApprovedProductImportResponse:
        results: list[BulkApprovedProductImportItem] = []
        for requested_id in payload.product_ids:
            item_session = sessionmaker(bind=self.db.get_bind(), expire_on_commit=False)()
            try:
                results.append(await self._import_candidate_item(item_session, payload.supplier, requested_id))
            except Exception as exc:
                item_session.rollback()
                results.append(
                    BulkApprovedProductImportItem(
                        requested_id=requested_id,
                        status="FAILED",
                        canonical_supplier_product_id=None,
                        product_id=None,
                        message=str(exc) or "Supplier candidate import failed",
                    )
                )
            finally:
                item_session.close()

        return BulkApprovedProductImportResponse(
            supplier=payload.supplier,
            requested_count=len(results),
            imported_count=sum(result.status == "IMPORTED" for result in results),
            already_exists_count=sum(result.status == "ALREADY_EXISTS" for result in results),
            already_imported_count=sum(result.status == "ALREADY_IMPORTED" for result in results),
            rejected_not_approved_count=sum(
                result.status == "REJECTED_NOT_APPROVED" for result in results
            ),
            failed_count=sum(result.status == "FAILED" for result in results),
            results=results,
        )

    async def _import_candidate_item(
        self, db: Session, supplier: str, requested_id: str
    ) -> BulkApprovedProductImportItem:
        candidate = db.scalar(
            select(SupplierCandidate).where(
                SupplierCandidate.supplier == supplier,
                SupplierCandidate.supplier_product_id == requested_id,
            )
        )
        if candidate is None:
            sku_matches = list(
                db.scalars(
                    select(SupplierCandidate)
                    .where(
                        SupplierCandidate.supplier == supplier,
                        SupplierCandidate.supplier_sku == requested_id,
                    )
                    .limit(2)
                )
            )
            if len(sku_matches) > 1:
                raise BadRequestError("Supplier SKU matches multiple candidates")
            candidate = sku_matches[0] if sku_matches else None

        if candidate is None or candidate.approval_status in {"REVIEW", "REJECTED"}:
            return BulkApprovedProductImportItem(
                requested_id=requested_id,
                status="REJECTED_NOT_APPROVED",
                canonical_supplier_product_id=candidate.supplier_product_id if candidate else None,
                product_id=candidate.imported_product_id if candidate else None,
                message="No approved supplier candidate exists for this identifier",
            )
        if candidate.approval_status == "IMPORTED" or candidate.imported_product_id:
            return BulkApprovedProductImportItem(
                requested_id=requested_id,
                status="ALREADY_IMPORTED",
                canonical_supplier_product_id=candidate.supplier_product_id,
                product_id=candidate.imported_product_id,
                message="Supplier candidate was already imported",
            )

        product = db.scalar(
            select(Product).where(
                Product.supplier == supplier,
                Product.supplier_product_id == candidate.supplier_product_id,
            )
        )
        if product:
            candidate.imported_product_id = product.id
            candidate.approval_status = "IMPORTED"
            candidate.imported_at = datetime.now(timezone.utc)
            candidate.import_result = "ALREADY_EXISTS"
            candidate.import_failure_reason = None
            db.commit()
            return BulkApprovedProductImportItem(
                requested_id=requested_id,
                status="ALREADY_EXISTS",
                canonical_supplier_product_id=candidate.supplier_product_id,
                product_id=product.id,
                message="Catalog product already exists; candidate was linked",
            )

        import_service = AdminProductService(db, self.launch_pricing_policy)
        try:
            imported = await import_service.import_product(
                ProductImportRequest(
                    supplier="cj",
                    supplier_product_id=candidate.supplier_product_id,
                    destination="IN",
                ),
                commit=False,
            )
            product = db.get(Product, imported.id)
            if product is None:
                raise RuntimeError("Imported product could not be loaded")
            product.status = "DRAFT"
            product.commercial_status = "APPROVED"
            product.approval_decided_at = candidate.approved_at
            product.approval_decided_by_user_id = candidate.approved_by_user_id
            product.approval_rejection_reason = None
            product.approval_evidence = {
                "source": "SUPPLIER_CANDIDATE_APPROVAL",
                "supplier_candidate_id": str(candidate.id),
                "supplier_validation_status": candidate.supplier_validation_status,
                "supplier_validation_score": candidate.supplier_validation_score,
                "market_status": candidate.market_status,
            }
            candidate.imported_product_id = product.id
            candidate.approval_status = "IMPORTED"
            candidate.imported_at = datetime.now(timezone.utc)
            candidate.import_result = "IMPORTED"
            candidate.import_failure_reason = None
            db.commit()
        except IntegrityError:
            db.rollback()
            product = db.scalar(
                select(Product).where(
                    Product.supplier == supplier,
                    Product.supplier_product_id == candidate.supplier_product_id,
                )
            )
            if product is None:
                raise
            candidate = db.get(SupplierCandidate, candidate.id)
            candidate.imported_product_id = product.id
            candidate.approval_status = "IMPORTED"
            candidate.imported_at = datetime.now(timezone.utc)
            candidate.import_result = "ALREADY_EXISTS"
            candidate.import_failure_reason = None
            db.commit()
            return BulkApprovedProductImportItem(
                requested_id=requested_id,
                status="ALREADY_EXISTS",
                canonical_supplier_product_id=candidate.supplier_product_id,
                product_id=product.id,
                message="Catalog product already exists; candidate was linked",
            )
        except Exception as exc:
            candidate.import_result = "FAILED"
            candidate.import_failure_reason = str(exc) or "Supplier candidate import failed"
            db.commit()
            raise

        return BulkApprovedProductImportItem(
            requested_id=requested_id,
            status="IMPORTED",
            canonical_supplier_product_id=candidate.supplier_product_id,
            product_id=product.id,
            message="Approved supplier candidate imported as DRAFT",
        )

    def update_status(self, product_id: UUID, payload: ProductStatusUpdate) -> AdminProductDTO:
        product = self._get(product_id)
        if payload.category_id is not None:
            if self.db.get(Category, payload.category_id) is None:
                raise NotFoundError("Category not found")
            product.category_id = payload.category_id
        if payload.brand_id is not None:
            if self.db.get(Brand, payload.brand_id) is None:
                raise NotFoundError("Brand not found")
            product.brand_id = payload.brand_id
        if payload.description is not None:
            product.description = payload.description.strip()
        if product.supplier:
            if payload.status != product.status:
                if payload.status != "DRAFT" or product.status != "DRAFT":
                    raise BadRequestError(
                        "Supplier-backed catalog status must use activate or pause actions"
                    )
                product.status = payload.status
            self.db.commit()
            return self._dto(product)
        product.status = payload.status
        self.db.commit()
        return self._dto(self._get(product.id))

    def calculate_price(
        self, product_id: UUID, payload: PriceCalculationRequest
    ) -> PriceCalculationResponse:
        product = self._get(product_id)
        if not product.supplier:
            raise BadRequestError("Catalog product has no supplier")
        if product.supplier_cost is None:
            raise BadRequestError("Supplier cost is missing")
        if product.shipping_cost is None:
            raise BadRequestError("Shipping cost is missing")

        try:
            calculation = calculate_margin_price(**payload.model_dump())
        except ValueError as exc:
            raise BadRequestError(str(exc)) from exc

        product.selling_price = calculation.selling_price_inr
        product.currency = "INR"
        self.db.commit()
        return PriceCalculationResponse(product_id=product.id, **calculation.__dict__)

    def calculate_variant_prices(self, product_id: UUID) -> VariantPriceCalculationResponse:
        product = self._get(product_id)
        if not product.supplier:
            raise BadRequestError("Catalog product has no supplier")
        if not product.variants:
            raise BadRequestError("Catalog product has no stored supplier variants")
        if product.shipping_cost is None:
            raise BadRequestError("Stored shipping cost is missing")
        if product.shipping_cost < 0:
            raise BadRequestError("Stored shipping cost must be nonnegative")

        variants = sorted(product.variants, key=lambda variant: variant.position)
        for variant in variants:
            if variant.supplier_cost_usd is None:
                raise BadRequestError(
                    f"Source USD supplier cost is missing for variant {variant.supplier_variant_id}"
                )
            if variant.supplier_cost_usd < 0:
                raise BadRequestError(
                    f"Source USD supplier cost must be nonnegative for variant {variant.supplier_variant_id}"
                )

        calculations: list[tuple[ProductVariant, VariantPriceCalculation]] = []
        for variant in variants:
            try:
                calculation = calculate_launch_variant_price(
                    supplier_cost_usd=variant.supplier_cost_usd,
                    shipping_cost_inr=product.shipping_cost,
                    policy=self.launch_pricing_policy,
                )
            except ValueError as exc:
                raise BadRequestError(str(exc)) from exc
            calculations.append((variant, VariantPriceCalculation(
                variant_id=variant.id,
                supplier_variant_id=variant.supplier_variant_id,
                **calculation.__dict__,
            )))

        for variant, calculation in calculations:
            variant.selling_price = calculation.selling_price_inr
        self.db.commit()
        return VariantPriceCalculationResponse(
            product_id=product.id,
            variants=[calculation for _, calculation in calculations],
        )

    def commercial_review(self, product_id: UUID) -> CommercialReviewResponse:
        product = self._get(product_id)
        if product.commercial_status in {"APPROVED", "REJECTED"}:
            raise BadRequestError("Final commercial decision already exists")
        result = evaluate_commercial_product(product, self.launch_pricing_policy)
        reviewed_at = datetime.now(timezone.utc)
        product.commercial_status = result.decision
        product.commercial_reasons = result.reasons
        product.commercial_reviewed_at = reviewed_at
        self.db.commit()
        return CommercialReviewResponse(
            product_id=product.id,
            reviewed_at=reviewed_at.isoformat(),
            **result.__dict__,
        )

    def approve(self, product_id: UUID, admin: User) -> AdminProductDTO:
        product = self._get(product_id)
        if not product.supplier or not product.supplier_product_id:
            raise BadRequestError("Final approval requires a supplier-backed catalog product")
        if product.status == "ACTIVE":
            raise BadRequestError("Active product is already past the approval gate")

        evaluation = evaluate_commercial_product(product, self.launch_pricing_policy)
        critical_blockers = [
            reason for reason in evaluation.blocking_reasons
            if reason != "SUPPLIER_VALIDATION_REVIEW"
        ]
        critical_blockers = list(dict.fromkeys(critical_blockers))
        if critical_blockers:
            raise BadRequestError(
                f"Final approval blocked: {', '.join(critical_blockers)}"
            )

        if product.commercial_status == "APPROVED":
            return self._dto(product)

        market_analysis = self.get_market_evidence(product.id).analysis
        decided_at = datetime.now(timezone.utc)
        product.commercial_status = "APPROVED"
        product.commercial_reasons = evaluation.reasons
        product.commercial_reviewed_at = decided_at
        product.approval_decided_at = decided_at
        product.approval_decided_by_user_id = admin.id
        product.approval_rejection_reason = None
        product.approval_evidence = self._approval_evidence_snapshot(
            product, evaluation, market_analysis, decided_at, admin, "APPROVED"
        )
        self.db.commit()
        return self._dto(self._get(product.id))

    def reject(
        self, product_id: UUID, payload: ProductRejectionRequest, admin: User
    ) -> AdminProductDTO:
        product = self._get(product_id)
        if not product.supplier or not product.supplier_product_id:
            raise BadRequestError("Final rejection requires a supplier-backed catalog product")
        if product.status == "ACTIVE":
            raise BadRequestError("Pause active product before rejection")
        if product.commercial_status == "DRAFT":
            raise BadRequestError("Run commercial review before final rejection")
        if (
            product.commercial_status == "REJECTED"
            and product.approval_rejection_reason == payload.reason
        ):
            return self._dto(product)

        evaluation = evaluate_commercial_product(product, self.launch_pricing_policy)
        market_analysis = self.get_market_evidence(product.id).analysis
        decided_at = datetime.now(timezone.utc)
        product.commercial_status = "REJECTED"
        product.commercial_reasons = list(dict.fromkeys(evaluation.reasons + ["HUMAN_REJECTED"]))
        product.commercial_reviewed_at = decided_at
        product.approval_decided_at = decided_at
        product.approval_decided_by_user_id = admin.id
        product.approval_rejection_reason = payload.reason
        product.approval_evidence = self._approval_evidence_snapshot(
            product, evaluation, market_analysis, decided_at, admin, "REJECTED"
        )
        self.db.commit()
        return self._dto(self._get(product.id))

    def activate(self, product_id: UUID) -> AdminProductDTO:
        product = self._get(product_id)
        if not product.supplier:
            raise BadRequestError("Activation gate applies to supplier-backed catalog products")
        if product.status == "ACTIVE":
            return self._dto(product)
        if product.status not in {"DRAFT", "PAUSED"}:
            raise BadRequestError(f"Cannot activate product from catalog status {product.status}")
        if product.commercial_status != "APPROVED":
            raise BadRequestError("Product must have commercial status APPROVED before activation")
        readiness = CatalogReadinessService.validate_activation(product)
        if not readiness.ready:
            raise BadRequestError(f"Catalog readiness failed: {', '.join(readiness.blocking_reasons)}")
        product.status = "ACTIVE"
        self.db.commit()
        return self._dto(self._get(product.id))

    def pause(self, product_id: UUID) -> AdminProductDTO:
        product = self._get(product_id)
        if not product.supplier:
            raise BadRequestError("Pause action applies to supplier-backed catalog products")
        if product.status == "PAUSED":
            return self._dto(product)
        if product.status != "ACTIVE":
            raise BadRequestError("Only an ACTIVE product can be paused")
        product.status = "PAUSED"
        self.db.commit()
        return self._dto(self._get(product.id))

    def create_market_evidence(
        self, product_id: UUID, payload: MarketEvidenceCreate
    ) -> MarketEvidenceDTO:
        product = self._get(product_id)
        evidence = ProductMarketEvidence(
            product_id=product.id,
            competitor_name=payload.competitor_name,
            product_name=payload.product_name,
            source_url=str(payload.source_url),
            observed_price_inr=payload.observed_price_inr,
            currency=payload.currency,
            variant_description=payload.variant_description,
            notes=payload.notes,
            checked_at=payload.checked_at or datetime.now(timezone.utc),
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return self._market_evidence_dto(evidence)

    def get_market_evidence(self, product_id: UUID) -> MarketEvidenceResponse:
        product = self._get(product_id)
        evidence = list(self.db.scalars(
            select(ProductMarketEvidence)
            .where(ProductMarketEvidence.product_id == product.id)
            .order_by(ProductMarketEvidence.checked_at.desc(), ProductMarketEvidence.created_at.desc())
        ).all())
        active_variant_prices = sorted(
            variant.selling_price
            for variant in product.variants
            if variant.active and variant.selling_price is not None
        )
        comparison_prices = (
            active_variant_prices
            if active_variant_prices
            else [product.selling_price] if product.selling_price is not None else []
        )

        return MarketEvidenceResponse(
            product_id=product.id,
            supplier_candidate_id=None,
            evidence=[self._market_evidence_dto(item) for item in evidence],
            analysis=self._analyze_market_evidence(
                evidence,
                comparison_prices,
                evaluated_variant_count=len(active_variant_prices),
                letrusto_variant_min_price_inr=active_variant_prices[0] if active_variant_prices else None,
                letrusto_variant_max_price_inr=active_variant_prices[-1] if active_variant_prices else None,
                stored_product_selling_price_inr=product.selling_price,
            ),
        )

    def delete_market_evidence(self, product_id: UUID, evidence_id: UUID) -> None:
        self._get(product_id)
        evidence = self.db.scalar(select(ProductMarketEvidence).where(
            ProductMarketEvidence.id == evidence_id,
            ProductMarketEvidence.product_id == product_id,
        ))
        if not evidence:
            raise NotFoundError("Market evidence not found for catalog product")
        self.db.delete(evidence)
        self.db.commit()

    def create_candidate_market_evidence(
        self, candidate_id: UUID, payload: MarketEvidenceCreate
    ) -> MarketEvidenceDTO:
        candidate = self._get_candidate(candidate_id)
        evidence = ProductMarketEvidence(
            supplier_candidate_id=candidate.id,
            competitor_name=payload.competitor_name,
            product_name=payload.product_name,
            source_url=str(payload.source_url),
            observed_price_inr=payload.observed_price_inr,
            currency=payload.currency,
            variant_description=payload.variant_description,
            notes=payload.notes,
            checked_at=payload.checked_at or datetime.now(timezone.utc),
        )
        self.db.add(evidence)
        self.db.flush()
        self._update_candidate_market_status(candidate)
        self.db.commit()
        self.db.refresh(evidence)
        return self._market_evidence_dto(evidence)

    def get_candidate_market_evidence(self, candidate_id: UUID) -> MarketEvidenceResponse:
        candidate = self._get_candidate(candidate_id)
        evidence = self._candidate_market_evidence(candidate.id)
        return MarketEvidenceResponse(
            product_id=None,
            supplier_candidate_id=candidate.id,
            evidence=[self._market_evidence_dto(item) for item in evidence],
            analysis=self._candidate_market_analysis(candidate, evidence),
        )

    def delete_candidate_market_evidence(self, candidate_id: UUID, evidence_id: UUID) -> None:
        candidate = self._get_candidate(candidate_id)
        evidence = self.db.scalar(select(ProductMarketEvidence).where(
            ProductMarketEvidence.id == evidence_id,
            ProductMarketEvidence.supplier_candidate_id == candidate.id,
        ))
        if not evidence:
            raise NotFoundError("Market evidence not found for supplier candidate")
        self.db.delete(evidence)
        self.db.flush()
        self._update_candidate_market_status(candidate)
        self.db.commit()

    async def sync_inventory(self, product_id: UUID) -> AdminProductDTO:
        product = self._get(product_id)
        if not product.supplier:
            raise BadRequestError("Catalog product has no supplier")
        if not product.supplier_product_id:
            raise BadRequestError("Catalog product has no supplier product ID")
        if not product.variants:
            raise BadRequestError("Catalog product has no stored supplier variants")

        try:
            adapter = build_supplier_adapter(product.supplier)
        except ValueError as exc:
            raise BadRequestError(str(exc)) from exc

        try:
            if not await adapter.authenticate():
                raise BadRequestError("Supplier authentication failed")
            if not await adapter.get_product(product.supplier_product_id, strict=True):
                raise NotFoundError("Supplier product not found")

            snapshots = []
            for variant in product.variants:
                snapshot = await adapter.get_inventory(variant.supplier_variant_id, strict=True)
                if snapshot is None:
                    raise BadRequestError(f"Inventory unavailable for supplier variant {variant.supplier_variant_id}")
                if any(
                    type(value) is not int or value < 0
                    for value in (snapshot.total_inventory, snapshot.cj_inventory, snapshot.factory_inventory)
                ):
                    raise BadRequestError(f"Malformed inventory for supplier variant {variant.supplier_variant_id}")
                snapshots.append((variant, snapshot))
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise BadRequestError("Supplier inventory synchronization failed") from exc

        for variant, snapshot in snapshots:
            variant.total_inventory = snapshot.total_inventory
            variant.cj_inventory = snapshot.cj_inventory
            variant.factory_inventory = snapshot.factory_inventory
            variant.verified_warehouse = snapshot.verification_status
            self._sync_variant_warehouse_inventory(product, variant, snapshot)

        product.total_inventory = sum(snapshot.total_inventory for _, snapshot in snapshots)
        product.cj_inventory = sum(snapshot.cj_inventory for _, snapshot in snapshots)
        product.factory_inventory = sum(snapshot.factory_inventory for _, snapshot in snapshots)
        product.verified_warehouse = (
            "verified" if any(snapshot.verification_status == "verified" for _, snapshot in snapshots)
            else next((snapshot.verification_status for _, snapshot in snapshots if snapshot.verification_status), None)
        )
        product.last_supplier_sync_at = datetime.now(timezone.utc)
        self.db.commit()
        return self._dto(self._get(product.id))

    def _sync_variant_warehouse_inventory(self, product, variant, snapshot) -> None:
        if not snapshot.warehouses:
            return
        identities = set()
        for warehouse in snapshot.warehouses:
            identity = warehouse.storage_id or f"{warehouse.warehouse_country}:{warehouse.warehouse_name or ''}"
            identities.add(identity)
            record = self.db.scalar(
                select(SupplierVariantInventory).where(
                    SupplierVariantInventory.supplier == product.supplier,
                    SupplierVariantInventory.supplier_variant_id == variant.supplier_variant_id,
                    SupplierVariantInventory.warehouse_identity == identity,
                )
            )
            if record is None:
                record = SupplierVariantInventory(
                    product_id=product.id,
                    variant_id=variant.id,
                    supplier=product.supplier or "",
                    supplier_product_id=product.supplier_product_id or "",
                    supplier_variant_id=variant.supplier_variant_id,
                    warehouse_identity=identity,
                )
                self.db.add(record)
            record.product_id = product.id
            record.variant_id = variant.id
            record.supplier_product_id = product.supplier_product_id or ""
            record.warehouse_country = warehouse.warehouse_country
            record.storage_id = warehouse.storage_id
            record.warehouse_name = warehouse.warehouse_name
            record.total_inventory = warehouse.total_inventory
            record.cj_sellable_inventory = warehouse.cj_inventory
            record.factory_inventory = warehouse.factory_inventory
            record.verification_status = warehouse.verification_status
            record.last_synced_at = datetime.now(timezone.utc)

        self.db.query(SupplierVariantInventory).filter(
            SupplierVariantInventory.variant_id == variant.id,
            SupplierVariantInventory.warehouse_identity.not_in(identities),
        ).delete(synchronize_session=False)

    async def revalidate_supplier(self, product_id: UUID) -> AdminProductDTO:
        product = self._get(product_id)
        if product.supplier != "cj" or not product.supplier_product_id:
            raise BadRequestError("Supplier revalidation requires a CJ-backed product")
        adapter = build_supplier_adapter(product.supplier)
        if not await adapter.authenticate():
            raise BadRequestError("Supplier authentication failed")
        raw = await adapter.get_product(product.supplier_product_id, strict=True)
        if raw is None:
            raise NotFoundError("Supplier product not found")
        config = EconomicsConfig()
        normalized = normalize_product(raw, usd_to_inr=config.usd_to_inr)
        shipping = None
        if normalized.variants:
            shipping = await adapter.calculate_shipping(
                normalized.variants[0].supplier_variant_id,
                "IN",
                origin_country=normalized.warehouse_country or "CN",
            )
        shipping_usd = shipping.options[0].cost_usd if shipping and shipping.options else None
        economics = calculate_economics(normalized, shipping_cost_usd=shipping_usd, config=config)
        result = score_product(normalized, economics=economics, shipping=shipping)
        validated_at = datetime.now(timezone.utc)
        product.supplier_validation_status = result.verdict.value
        product.supplier_validation_score = result.score
        product.supplier_validation_notes = result.notes
        product.supplier_validated_at = validated_at
        product.supplier_validation_details = {
            "calculation_origin": "REVALIDATION",
            "source_price_usd": normalized.cost_usd,
            "source_weight_grams": normalized.weight_grams,
            "missing_fields": normalized.missing_fields,
            "shipping_validation": shipping.validation.value if shipping else None,
            "shipping_cost_usd": shipping_usd,
            "score_breakdown": result.breakdown.__dict__,
        }
        candidate = self.db.scalar(select(SupplierCandidate).where(
            SupplierCandidate.supplier == product.supplier,
            SupplierCandidate.supplier_product_id == product.supplier_product_id,
        ))
        if candidate is not None:
            candidate.supplier_validation_status = result.verdict.value
            candidate.supplier_validation_score = result.score
        self.db.commit()
        return self._dto(self._get(product.id))

    def _get(self, product_id: UUID) -> Product:
        stmt = select(Product).options(selectinload(Product.images), selectinload(Product.variants)).where(Product.id == product_id)
        product = self.db.scalars(stmt).unique().first()
        if not product:
            raise NotFoundError("Catalog product not found")
        return product

    def _get_candidate(self, candidate_id: UUID) -> SupplierCandidate:
        candidate = self.db.get(SupplierCandidate, candidate_id)
        if not candidate:
            raise NotFoundError("Supplier candidate not found")
        return candidate

    def get_supplier_candidate(self, candidate_id: UUID) -> SupplierCandidateDTO:
        return self._candidate_dto(self._get_candidate(candidate_id))

    @staticmethod
    def _candidate_dto(candidate: SupplierCandidate) -> SupplierCandidateDTO:
        snapshot = candidate.data_snapshot or {}
        return SupplierCandidateDTO(
            id=candidate.id,
            supplier=candidate.supplier,
            supplier_product_id=candidate.supplier_product_id,
            supplier_sku=candidate.supplier_sku,
            name=candidate.name,
            approval_status=candidate.approval_status,
            supplier_validation_status=candidate.supplier_validation_status,
            supplier_validation_score=candidate.supplier_validation_score,
            commercial_status=candidate.commercial_status,
            market_status=candidate.market_status,
            discovery_min_selling_price_inr=candidate.discovery_min_selling_price_inr,
            discovery_max_selling_price_inr=candidate.discovery_max_selling_price_inr,
            snapshot_status=candidate.snapshot_status,
            main_image=snapshot.get("main_image"),
            variants=snapshot.get("variants", []),
            validation_issues=snapshot.get("validation_issues", []),
            target_margin_percent=snapshot.get("target_margin_percent"),
            target_cac_inr=snapshot.get("target_cac_inr"),
            cac_viable=snapshot.get("cac_viable"),
            market_evidence_count=len(candidate.market_evidence),
            approved_at=candidate.approved_at,
            approved_by_user_id=candidate.approved_by_user_id,
            decision_at=candidate.decision_at,
            decision_by_user_id=candidate.decision_by_user_id,
            rejection_reason=candidate.rejection_reason,
            imported_product_id=candidate.imported_product_id,
            imported_at=candidate.imported_at,
            import_result=candidate.import_result,
            import_failure_reason=candidate.import_failure_reason,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
        )

    def _unique_slug(self, title: str, supplier_product_id: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "supplier-product"
        return f"{base}-{supplier_product_id.lower()}"[:150]

    @staticmethod
    def _market_evidence_dto(evidence: ProductMarketEvidence) -> MarketEvidenceDTO:
        return MarketEvidenceDTO(
            id=evidence.id,
            product_id=evidence.product_id,
            supplier_candidate_id=evidence.supplier_candidate_id,
            competitor_name=evidence.competitor_name,
            product_name=evidence.product_name,
            source_url=evidence.source_url,
            observed_price_inr=evidence.observed_price_inr,
            currency="INR",
            variant_description=evidence.variant_description,
            notes=evidence.notes,
            checked_at=evidence.checked_at,
            created_at=evidence.created_at,
            updated_at=evidence.updated_at,
        )

    @staticmethod
    def _analyze_market_evidence(
        evidence: list[ProductMarketEvidence],
        comparison_prices: list[Decimal],
        *,
        evaluated_variant_count: int,
        letrusto_variant_min_price_inr: Decimal | None,
        letrusto_variant_max_price_inr: Decimal | None,
        stored_product_selling_price_inr: Decimal | None,
        sufficient_without_comparison_status: str = "MARKET_COMPETITIVE",
    ) -> MarketEvidenceAnalysis:
        prices = sorted(item.observed_price_inr for item in evidence)
        count = len(prices)
        minimum = prices[0] if prices else None
        maximum = prices[-1] if prices else None
        average = (
            (sum(prices, Decimal("0")) / Decimal(count)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if prices else None
        )
        if not prices:
            median = None
        elif count % 2:
            median = prices[count // 2]
        else:
            median = ((prices[count // 2 - 1] + prices[count // 2]) / Decimal("2")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        if count < 2:
            status = "INSUFFICIENT_MARKET_DATA"
        elif comparison_prices and all(price > maximum for price in comparison_prices):
            status = "MARKET_ABOVE_OBSERVED"
        elif not comparison_prices:
            status = sufficient_without_comparison_status
        else:
            status = "MARKET_COMPETITIVE"
        return MarketEvidenceAnalysis(
            observation_count=count,
            minimum_price_inr=minimum,
            maximum_price_inr=maximum,
            average_price_inr=average,
            median_price_inr=median,
            status=status,
            evaluated_variant_count=evaluated_variant_count,
            letrusto_variant_min_price_inr=letrusto_variant_min_price_inr,
            letrusto_variant_max_price_inr=letrusto_variant_max_price_inr,
            stored_product_selling_price_inr=stored_product_selling_price_inr,
        )

    def _candidate_market_evidence(self, candidate_id: UUID) -> list[ProductMarketEvidence]:
        return list(self.db.scalars(
            select(ProductMarketEvidence)
            .where(ProductMarketEvidence.supplier_candidate_id == candidate_id)
            .order_by(ProductMarketEvidence.checked_at.desc(), ProductMarketEvidence.created_at.desc())
        ).all())

    def _candidate_market_analysis(
        self, candidate: SupplierCandidate, evidence: list[ProductMarketEvidence]
    ) -> MarketEvidenceAnalysis:
        has_price_range = (
            candidate.discovery_min_selling_price_inr is not None
            and candidate.discovery_max_selling_price_inr is not None
        )
        comparison_prices = (
            [candidate.discovery_min_selling_price_inr, candidate.discovery_max_selling_price_inr]
            if has_price_range else []
        )
        return self._analyze_market_evidence(
            evidence,
            comparison_prices,
            evaluated_variant_count=0,
            letrusto_variant_min_price_inr=candidate.discovery_min_selling_price_inr,
            letrusto_variant_max_price_inr=candidate.discovery_max_selling_price_inr,
            stored_product_selling_price_inr=None,
            sufficient_without_comparison_status="MARKET_EVIDENCE_AVAILABLE",
        )

    def _update_candidate_market_status(self, candidate: SupplierCandidate) -> None:
        candidate.market_status = self._candidate_market_analysis(
            candidate, self._candidate_market_evidence(candidate.id)
        ).status

    def _approval_evidence_snapshot(
        self,
        product: Product,
        evaluation,
        market_analysis: MarketEvidenceAnalysis,
        decided_at: datetime,
        admin: User,
        decision: str,
    ) -> dict:
        active_prices = sorted(
            variant.selling_price
            for variant in product.variants
            if variant.active and variant.selling_price is not None
        )
        return {
            "decision": decision,
            "decided_at": decided_at.isoformat(),
            "decided_by_user_id": str(admin.id),
            "supplier_validation": {
                "status": product.supplier_validation_status,
                "score": product.supplier_validation_score,
                "validated_at": (
                    product.supplier_validated_at.isoformat() if product.supplier_validated_at else None
                ),
            },
            "pricing_policy": {
                "identifier": "PHASE_3_3_LAUNCH_POLICY",
                "fx_rate": str(self.launch_pricing_policy.pricing_fx_rate),
                "payment_gateway_percent": str(self.launch_pricing_policy.payment_gateway_pct),
                "rto_reserve_percent": str(self.launch_pricing_policy.rto_reserve_pct),
                "target_margin_percent": str(
                    self.launch_pricing_policy.target_contribution_margin_pct
                ),
                "target_cac_inr": str(self.launch_pricing_policy.target_cac_inr),
            },
            "variants": {
                "active_count": evaluation.active_variant_count,
                "priced_count": len(active_prices),
                "minimum_price_inr": str(active_prices[0]) if active_prices else None,
                "maximum_price_inr": str(active_prices[-1]) if active_prices else None,
            },
            "market_evidence": {
                "count": market_analysis.observation_count,
                "minimum_price_inr": (
                    str(market_analysis.minimum_price_inr)
                    if market_analysis.minimum_price_inr is not None else None
                ),
                "maximum_price_inr": (
                    str(market_analysis.maximum_price_inr)
                    if market_analysis.maximum_price_inr is not None else None
                ),
                "average_price_inr": (
                    str(market_analysis.average_price_inr)
                    if market_analysis.average_price_inr is not None else None
                ),
                "median_price_inr": (
                    str(market_analysis.median_price_inr)
                    if market_analysis.median_price_inr is not None else None
                ),
                "status": market_analysis.status,
            },
            "cac_status": evaluation.cac_target_status,
            "commercial_reasons": evaluation.reasons,
            "cj_inventory": product.cj_inventory,
        }

    def _dto(self, product: Product) -> AdminProductDTO:
        return AdminProductDTO(
            id=product.id, slug=product.slug, name=product.name, description=product.description, status=product.status,
            supplier=product.supplier, supplier_product_id=product.supplier_product_id, supplier_source_url=product.supplier_source_url,
            category_id=product.category_id, brand_id=product.brand_id,
            supplier_cost=product.supplier_cost, shipping_cost=product.shipping_cost, selling_price=product.selling_price,
            currency=product.currency, total_inventory=product.total_inventory, cj_inventory=product.cj_inventory,
            factory_inventory=product.factory_inventory, verified_warehouse=product.verified_warehouse,
            last_supplier_sync_at=product.last_supplier_sync_at.isoformat() if product.last_supplier_sync_at else None,
            commercial_status=product.commercial_status,
            commercial_reasons=product.commercial_reasons or [],
            commercial_reviewed_at=product.commercial_reviewed_at.isoformat() if product.commercial_reviewed_at else None,
            commercial_target_margin_percent=self.launch_pricing_policy.target_contribution_margin_pct,
            commercial_target_cac_inr=self.launch_pricing_policy.target_cac_inr,
            commercial_cac_supported=(
                None if product.commercial_reviewed_at is None
                else "CAC_TARGET_NOT_SUPPORTED" not in (product.commercial_reasons or [])
            ),
            supplier_validation_status=product.supplier_validation_status,
            supplier_validation_score=product.supplier_validation_score,
            supplier_validation_notes=product.supplier_validation_notes or [],
            supplier_validation_details=product.supplier_validation_details,
            supplier_validated_at=product.supplier_validated_at.isoformat() if product.supplier_validated_at else None,
            approval_decided_at=product.approval_decided_at.isoformat() if product.approval_decided_at else None,
            approval_decided_by_user_id=product.approval_decided_by_user_id,
            approval_rejection_reason=product.approval_rejection_reason,
            approval_evidence=product.approval_evidence,
            images=[image.url for image in sorted(product.images, key=lambda item: item.position)],
            variants=[AdminProductVariantDTO(
                id=variant.id, supplier_variant_id=variant.supplier_variant_id, supplier_variant_sku=variant.supplier_variant_sku,
                name=variant.name, attributes=variant.attributes, supplier_cost=variant.supplier_cost,
                supplier_cost_usd=variant.supplier_cost_usd,
                selling_price=variant.selling_price,
                total_inventory=variant.total_inventory, cj_inventory=variant.cj_inventory, factory_inventory=variant.factory_inventory,
                verified_warehouse=variant.verified_warehouse, weight_grams=variant.weight_grams, active=variant.active, position=variant.position,
            ) for variant in sorted(product.variants, key=lambda item: item.position)],
        )