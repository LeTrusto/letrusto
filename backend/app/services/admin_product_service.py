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
    CartItem,
    Product,
    ProductFeature,
    ProductImage,
    ProductMarketEvidence,
    ProductSpecification,
    ProductTag,
    ProductVariant,
    SupplierCandidate,
    SupplierVariantInventory,
    User,
)
from app.schemas.admin_products import (
    AdminProductDTO,
    AdminProductInventoryResponse,
    AdminProductListResponse,
    AdminVariantInventoryDTO,
    AdminWarehouseInventoryDTO,
    AdminProductVariantDTO,
    BulkApprovedProductImportItem,
    BulkApprovedProductImportRequest,
    BulkApprovedProductImportResponse,
    CommercialReviewResponse,
    MarketEvidenceAnalysis,
    MarketEvidenceCreate,
    MarketEvidenceDTO,
    MarketEvidenceResponse,
    LegacyArchiveResponse,
    PriceCalculationRequest,
    PriceCalculationResponse,
    PrintfulConnectionResponse,
    PrintfulProductSummary,
    PrintfulProductsResponse,
    ProductImportRequest,
    ProductRejectionRequest,
    ProductStatusUpdate,
    SupplierCandidateCreate,
    SupplierCandidateDiscoveryItem,
    SupplierCandidateDiscoveryRequest,
    SupplierCandidateDiscoveryResponse,
    SupplierCandidateDTO,
    SupplierCandidateListResponse,
    VariantPriceCalculation,
    VariantPriceCalculationResponse,
)
from app.services.commercial_review_service import evaluate_commercial_product
from app.services.launch_pricing_policy import LaunchPricingPolicy, load_launch_pricing_policy
from app.services.pricing_engine import calculate_launch_variant_price, calculate_margin_price
from app.services.supplier_candidate_readiness_service import SupplierCandidateReadinessService
from app.suppliers.economics import EconomicsConfig, calculate_economics
from app.suppliers.base import InventorySnapshot, WarehouseInventorySnapshot
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
        active_supplier = supplier or "printful"
        stmt = stmt.where(Product.supplier == active_supplier)
        count_stmt = count_stmt.where(Product.supplier == active_supplier)
        if status:
            stmt = stmt.where(Product.status == status)
            count_stmt = count_stmt.where(Product.status == status)
        products = list(self.db.scalars(stmt.offset(skip).limit(limit)).unique().all())
        return AdminProductListResponse(products=[self._dto(p) for p in products], total=self.db.scalar(count_stmt) or 0)

    def archive_legacy_cj_products(self) -> LegacyArchiveResponse:
        products = list(self.db.scalars(select(Product).where(Product.supplier == "cj", Product.status == "ACTIVE")).all())
        for product in products:
            product.status = "PAUSED"
            product.last_supplier_sync_at = datetime.now(timezone.utc)
        self.db.commit()
        return LegacyArchiveResponse(supplier="cj", archived_count=len(products))

    async def test_printful_connection(self) -> PrintfulConnectionResponse:
        try:
            adapter = build_supplier_adapter("printful")
            if not hasattr(adapter, "connection_status"):
                raise BadRequestError("Printful adapter does not support connection checks")
            status = await adapter.connection_status()  # type: ignore[attr-defined]
        except ValueError as exc:
            return PrintfulConnectionResponse(connected=False, status="Missing configuration", message=str(exc))
        except httpx.HTTPStatusError as exc:
            message = "Printful authentication failed" if exc.response.status_code in {401, 403} else "Printful API request failed"
            return PrintfulConnectionResponse(connected=False, status="Unavailable", message=message)
        except (httpx.HTTPError, TypeError):
            return PrintfulConnectionResponse(connected=False, status="Unavailable", message="Printful API is not reachable")
        return PrintfulConnectionResponse(connected=True, store=status.get("store"), status=status.get("health", "Healthy"))

    async def list_printful_products(self) -> PrintfulProductsResponse:
        adapter = build_supplier_adapter("printful")
        if not hasattr(adapter, "list_finalized_store_products"):
            raise BadRequestError("Printful adapter does not support product discovery")
        products = await adapter.list_finalized_store_products()  # type: ignore[attr-defined]
        summaries: list[PrintfulProductSummary] = []
        for product in products:
            existing = self.db.scalar(
                select(Product.id).where(Product.supplier == "printful", Product.supplier_product_id == product.supplier_product_id)
            )
            summaries.append(PrintfulProductSummary(
                supplier_product_id=product.supplier_product_id,
                name=product.title,
                thumbnail_url=product.images[0] if product.images else None,
                finalized=True,
                imported_product_id=existing,
            ))
        return PrintfulProductsResponse(products=summaries, total=len(summaries))

    def get_product(self, product_id: UUID) -> AdminProductDTO:
        return self._dto(self._get(product_id))

    def delete_product(self, product_id: UUID) -> None:
        product = self.db.scalar(select(Product).where(Product.id == product_id).with_for_update())
        if product is None:
            raise NotFoundError("Product not found")
        order_count = self.db.scalar(select(func.count()).select_from(OrderItem).where(OrderItem.product_id == product_id)) or 0
        cart_count = self.db.scalar(select(func.count()).select_from(CartItem).where(CartItem.product_id == product_id)) or 0
        if order_count or cart_count:
            raise BadRequestError(
                f"Product cannot be deleted because it is referenced by {order_count} order item(s) and {cart_count} cart item(s)"
            )
        self.db.delete(product)
        self.db.commit()

    def get_inventory(self, product_id: UUID) -> AdminProductInventoryResponse:
        product = self.db.scalar(
            select(Product)
            .options(selectinload(Product.variants).selectinload(ProductVariant.warehouse_inventory))
            .where(Product.id == product_id)
        )
        if product is None:
            raise NotFoundError("Product not found")

        variants = []
        for variant in sorted(product.variants, key=lambda item: item.position):
            warehouses = [
                AdminWarehouseInventoryDTO(
                    product_id=product.id,
                    variant_id=variant.id,
                    vid=variant.supplier_variant_id,
                    sku=variant.supplier_variant_sku,
                    sellable_cj_inventory=warehouse.cj_sellable_inventory,
                    factory_inventory=warehouse.factory_inventory,
                    total_inventory=warehouse.total_inventory,
                    warehouse_country=warehouse.warehouse_country,
                    warehouse_name=warehouse.warehouse_name,
                    storage_id=warehouse.storage_id,
                    last_synced_at=warehouse.last_synced_at,
                )
                for warehouse in sorted(
                    variant.warehouse_inventory,
                    key=lambda item: (item.warehouse_country, item.warehouse_name or "", item.storage_id or ""),
                )
            ]
            variants.append(
                AdminVariantInventoryDTO(
                    product_id=product.id,
                    variant_id=variant.id,
                    vid=variant.supplier_variant_id,
                    sku=variant.supplier_variant_sku,
                    sellable_cj_inventory=variant.cj_inventory or 0,
                    factory_inventory=variant.factory_inventory or 0,
                    total_inventory=variant.total_inventory or 0,
                    warehouses=warehouses,
                )
            )
        return AdminProductInventoryResponse(product_id=product.id, variants=variants)

    async def import_product(self, payload: ProductImportRequest, *, commit: bool = True) -> AdminProductDTO:
        if payload.supplier == "printful":
            return await self._import_printful_product(payload.supplier_product_id, commit=commit)

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
        stored_variants = []
        for position, variant in enumerate(normalized.variants, start=1):
            stored_variant = ProductVariant(
                product_id=product.id, supplier_variant_id=variant.supplier_variant_id,
                supplier_variant_sku=variant.supplier_variant_sku, name=variant.name,
                attributes=variant.option_key, supplier_cost=Decimal(str(variant.cost_inr)) if variant.cost_inr is not None else None,
                supplier_cost_usd=Decimal(str(variant.cost_usd)) if variant.cost_usd is not None else None,
                total_inventory=variant.total_inventory, cj_inventory=variant.cj_inventory,
                factory_inventory=variant.factory_inventory, verified_warehouse=variant.inventory_verification,
                weight_grams=Decimal(str(variant.weight_grams)) if variant.weight_grams is not None else None, position=position,
            )
            self.db.add(stored_variant)
            stored_variants.append((stored_variant, variant))
        self.db.flush()
        for stored_variant, variant in stored_variants:
            self._sync_variant_warehouse_inventory(
                product,
                stored_variant,
                InventorySnapshot(
                    total_inventory=variant.total_inventory or 0,
                    cj_inventory=variant.cj_inventory or 0,
                    factory_inventory=variant.factory_inventory or 0,
                    verification_status=variant.inventory_verification,
                    warehouses=variant.warehouses,
                ),
            )
        if commit:
            self.db.commit()
        else:
            self.db.flush()
        return self._dto(self._get(product.id))

    async def import_printful_hoodie(self, supplier_product_id: str) -> AdminProductDTO:
        return await self._import_printful_product(supplier_product_id, require_hoodie=True)

    async def _import_printful_product(self, supplier_product_id: str, *, require_hoodie: bool = False, commit: bool = True) -> AdminProductDTO:
        adapter = build_supplier_adapter("printful")
        if not await adapter.authenticate():
            raise BadRequestError("Printful connection failed")
        raw = await adapter.get_product(supplier_product_id)
        if not raw:
            raise NotFoundError("Printful product not found")
        if require_hoodie and raw.title.strip().lower() != "unisex hoodie":
            raise BadRequestError("First Printful import is restricted to Unisex Hoodie")
        if not raw.variants:
            raise BadRequestError("Printful product has no usable variants")

        config = EconomicsConfig()
        normalized = normalize_product(raw, usd_to_inr=config.usd_to_inr, derive_variant_fields=True)
        product = self.db.scalar(
            select(Product)
            .options(selectinload(Product.images), selectinload(Product.variants))
            .where(Product.supplier == "printful", Product.supplier_product_id == normalized.supplier_product_id)
        )
        if product is None:
            product = Product(id=uuid4(), slug=self._unique_slug(normalized.title, normalized.supplier_product_id))
            self.db.add(product)
        variant_costs_usd = [Decimal(str(variant.cost_usd)) for variant in normalized.variants if variant.cost_usd is not None]
        supplier_cost_usd = min(variant_costs_usd) if variant_costs_usd else None
        supplier_cost_inr = supplier_cost_usd * Decimal(str(config.usd_to_inr)) if supplier_cost_usd is not None else None

        product.name = normalized.title
        product.description = normalized.description or normalized.title
        product.status = "DRAFT"
        product.supplier = "printful"
        product.supplier_product_id = normalized.supplier_product_id
        product.supplier_source_url = f"https://www.printful.com/dashboard/store/products/{normalized.supplier_product_id}"
        product.supplier_cost = supplier_cost_inr.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if supplier_cost_inr is not None else None
        product.shipping_cost = None
        product.selling_price = None
        product.currency = "INR"
        product.total_inventory = normalized.total_inventory
        product.cj_inventory = normalized.cj_inventory
        product.factory_inventory = normalized.factory_inventory
        product.verified_warehouse = normalized.inventory_verification
        product.last_supplier_sync_at = datetime.now(timezone.utc)
        product.supplier_validation_status = "REVIEW"
        product.supplier_validation_score = None
        product.supplier_validation_notes = ["PRINTFUL_POD_REVIEW_REQUIRED"]
        product.supplier_validated_at = datetime.now(timezone.utc)
        product.supplier_validation_details = {
            "source": "PRINTFUL_SYNC_PRODUCT_IMPORT",
            "sync_product_id": normalized.supplier_product_id,
            "reference_data": raw.raw_payload or {},
            "variants": [
                {
                    "sync_variant_id": variant.supplier_variant_id,
                    "supplier_variant_sku": variant.supplier_variant_sku,
                    "attributes": variant.option_key,
                    "supplier_cost_usd": variant.cost_usd,
                    "availability": variant.inventory_verification,
                }
                for variant in normalized.variants
            ],
        }
        self.db.flush()

        self.db.query(ProductImage).filter(ProductImage.product_id == product.id).delete(synchronize_session=False)
        for position, image_url in enumerate(normalized.images, start=1):
            if image_url:
                self.db.add(ProductImage(product_id=product.id, url=image_url, position=position))

        existing_variants = {variant.supplier_variant_id: variant for variant in product.variants}
        for position, variant in enumerate(normalized.variants, start=1):
            stored_variant = existing_variants.get(variant.supplier_variant_id)
            if stored_variant is None:
                stored_variant = ProductVariant(product_id=product.id, supplier_variant_id=variant.supplier_variant_id)
                self.db.add(stored_variant)
            stored_variant.supplier_variant_sku = variant.supplier_variant_sku
            stored_variant.name = variant.name
            stored_variant.attributes = variant.option_key
            stored_variant.supplier_cost = Decimal(str(variant.cost_inr)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if variant.cost_inr is not None else None
            stored_variant.supplier_cost_usd = Decimal(str(variant.cost_usd)) if variant.cost_usd is not None else None
            stored_variant.total_inventory = variant.total_inventory
            stored_variant.cj_inventory = variant.cj_inventory
            stored_variant.factory_inventory = variant.factory_inventory
            stored_variant.verified_warehouse = variant.inventory_verification
            stored_variant.weight_grams = Decimal(str(variant.weight_grams)) if variant.weight_grams is not None else None
            stored_variant.active = True
            stored_variant.position = position
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
        failure_reasons: list[str] = []
        if not normalized.variants:
            failure_reasons.append("MISSING_VID")
        variant_ids = [variant.supplier_variant_id.strip() for variant in normalized.variants]
        if any(not variant_id for variant_id in variant_ids):
            failure_reasons.append("MISSING_VID")
        if len(set(variant_ids)) != len(variant_ids):
            failure_reasons.append("INVALID_PRODUCT_VARIANT_RELATIONSHIP")
        sellable_inventory = sum((variant.cj_inventory or 0) for variant in normalized.variants)
        if sellable_inventory <= 0:
            failure_reasons.append("NO_SELLABLE_INVENTORY")
        if not shipping or not shipping.can_ship:
            failure_reasons.append("NO_INDIA_SHIPPING_ROUTE")
        selected_shipping = shipping.options[0] if shipping and shipping.options else None
        if not selected_shipping or not selected_shipping.carrier.strip() or not selected_shipping.method.strip():
            failure_reasons.append("MISSING_LOGISTICS")
        if selected_shipping and selected_shipping.cost_usd < 0:
            failure_reasons.append("INVALID_FREIGHT_COST")

        economics = calculate_economics(normalized, shipping_cost_usd=shipping_usd, config=config)
        product_score = score_product(normalized, economics=economics, shipping=shipping)
        if product_score.verdict.value == "REJECT":
            failure_reasons.extend(product_score.notes)
        shipping_cost_inr = Decimal(str(shipping_usd * config.usd_to_inr)) if shipping_usd is not None else Decimal("0")
        variant_snapshot = []
        for variant in normalized.variants:
            price = None
            try:
                if variant.cost_usd is None:
                    raise ValueError("MISSING_VARIANT_COST")
                price = calculate_launch_variant_price(
                    supplier_cost_usd=Decimal(str(variant.cost_usd)),
                    shipping_cost_inr=shipping_cost_inr,
                    policy=self.launch_pricing_policy,
                )
            except (ValueError, TypeError) as exc:
                failure_reasons.append(str(exc) or "PRICING_FAILURE")
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
                "vid": variant.supplier_variant_id,
                "sku": variant.supplier_variant_sku,
                "warehouses": [warehouse.__dict__ for warehouse in variant.warehouses],
            })
        selling_prices = [Decimal(item["selling_price_inr"]) for item in variant_snapshot if item["selling_price_inr"]]
        failure_reasons = list(dict.fromkeys(failure_reasons))
        requested_readiness = "REJECTED" if failure_reasons else (
            "VALIDATED" if product_score.verdict.value == "PASS" else "REVIEW"
        )
        readiness_status = SupplierCandidateReadinessService.initial_state(requested_readiness)
        logistics = {
            "available": bool(shipping and shipping.options),
            "validation": getattr(shipping.validation, "value", shipping.validation) if shipping else None,
            "origin_country": shipping.origin_country if shipping else None,
            "destination_country": shipping.destination_country if shipping else payload.destination,
            "selected": shipping.options[0].__dict__ if shipping and shipping.options else None,
            "options": [option.__dict__ for option in shipping.options] if shipping else [],
        }
        warehouses = [
            {**warehouse.__dict__, "supplier_variant_id": variant.supplier_variant_id}
            for variant in normalized.variants
            for warehouse in variant.warehouses
        ]

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
            readiness_status=readiness_status,
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
                "reference_data": raw.raw_payload or {},
                "warehouses": warehouses,
                "logistics": logistics,
                "freight": {
                    "available": bool(shipping and shipping.options),
                    "cost_usd": shipping_usd,
                    "cost_inr": str(shipping_cost_inr) if shipping_usd is not None else None,
                    "delivery_estimate": shipping.options[0].estimated_days if shipping and shipping.options else None,
                },
                "commercial_result": {
                    "minimum_price_inr": str(min(selling_prices)) if selling_prices else None,
                    "maximum_price_inr": str(max(selling_prices)) if selling_prices else None,
                    "target_margin_percent": str(self.launch_pricing_policy.target_contribution_margin_pct),
                    "cac_viable": all(item["cac_target_status"] == "CAC_TARGET_SUPPORTED" for item in variant_snapshot if item["cac_target_status"]),
                    "failure_reasons": failure_reasons,
                },
                "validation_issues": list(dict.fromkeys(product_score.notes + failure_reasons)),
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

    async def discover_supplier_candidates(
        self, payload: SupplierCandidateDiscoveryRequest
    ) -> SupplierCandidateDiscoveryResponse:
        adapter = build_supplier_adapter(payload.supplier)
        if not await adapter.authenticate():
            raise BadRequestError("Supplier authentication failed")
        search_results = await adapter.search_products(payload.keyword, page_size=payload.page_size)
        results: list[SupplierCandidateDiscoveryItem] = []
        seen_ids: set[str] = set()
        for search_item in search_results:
            product_id = search_item.supplier_product_id.strip()
            if not product_id or product_id in seen_ids:
                continue
            seen_ids.add(product_id)
            try:
                existing = self.db.scalar(
                    select(SupplierCandidate).where(
                        SupplierCandidate.supplier == payload.supplier,
                        SupplierCandidate.supplier_product_id == product_id,
                    )
                )
                if existing:
                    results.append(SupplierCandidateDiscoveryItem(
                        supplier_product_id=product_id,
                        title=search_item.title,
                        status="ALREADY_STAGED",
                        candidate=self._candidate_dto(existing),
                    ))
                    continue
                candidate = await self.create_supplier_candidate(SupplierCandidateCreate(
                    supplier=payload.supplier,
                    supplier_product_id=product_id,
                    destination=payload.destination,
                ))
                results.append(SupplierCandidateDiscoveryItem(
                    supplier_product_id=product_id,
                    title=search_item.title,
                    status="STAGED",
                    candidate=candidate,
                ))
            except Exception as exc:
                self.db.rollback()
                results.append(SupplierCandidateDiscoveryItem(
                    supplier_product_id=product_id,
                    title=search_item.title,
                    status="FAILED",
                    message=str(exc) or "Supplier candidate discovery failed",
                ))
        return SupplierCandidateDiscoveryResponse(
            supplier=payload.supplier,
            keyword=payload.keyword,
            destination=payload.destination,
            requested_count=len(search_results),
            staged_count=sum(item.status == "STAGED" for item in results),
            already_staged_count=sum(item.status == "ALREADY_STAGED" for item in results),
            failed_count=sum(item.status == "FAILED" for item in results),
            results=results,
        )

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
        if candidate.readiness_status == "REJECTED":
            raise BadRequestError("Deterministic readiness gates rejected this supplier candidate")
        if candidate.supplier_validation_status == "REJECT":
            raise BadRequestError("Supplier candidate rejected by supplier validation cannot be approved")
        enrichment = (candidate.data_snapshot or {}).get("enrichment") or {}
        if enrichment.get("status") != "ENRICHED":
            raise BadRequestError("Supplier candidate requires successful enrichment before approval")
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

    def transition_supplier_candidate_readiness(
        self, candidate_id: UUID, target: str
    ) -> SupplierCandidateDTO:
        candidate = self._get_candidate(candidate_id)
        candidate.readiness_status = SupplierCandidateReadinessService.transition(
            candidate.readiness_status, target  # type: ignore[arg-type]
        )
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

    async def import_supplier_candidate(self, candidate_id: UUID) -> AdminProductDTO:
        try:
            return await self._import_supplier_candidate(candidate_id)
        except Exception:
            self.db.rollback()
            raise

    async def _import_supplier_candidate(self, candidate_id: UUID) -> AdminProductDTO:
        candidate = self._get_candidate(candidate_id)
        if candidate.imported_product_id or candidate.approval_status == "IMPORTED":
            if candidate.imported_product_id:
                return self._dto(self._get(candidate.imported_product_id))
            raise BadRequestError("Imported supplier candidate has no catalog product")

        if candidate.approval_status == "REJECTED" or candidate.readiness_status == "REJECTED":
            raise BadRequestError("Rejected supplier candidate cannot be imported")
        if candidate.approval_status != "APPROVED":
            raise BadRequestError("Supplier candidate requires explicit admin approval")

        snapshot = candidate.data_snapshot or {}
        enrichment = snapshot.get("enrichment") or {}
        if enrichment.get("status") != "ENRICHED":
            raise BadRequestError("Successful enrichment is required before import")

        variants = snapshot.get("variants")
        reference = snapshot.get("reference_data")
        commercial = snapshot.get("commercial_result")
        if not isinstance(reference, dict) or not isinstance(variants, list) or not variants:
            raise BadRequestError("Required supplier product data is missing")
        if not isinstance(commercial, dict) or commercial.get("minimum_price_inr") is None:
            raise BadRequestError("Deterministic commercial result is missing")

        prepared_variants = self._prepare_candidate_variants(variants, commercial)
        existing = self.db.scalar(
            select(Product).where(
                Product.supplier == candidate.supplier,
                Product.supplier_product_id == candidate.supplier_product_id,
            )
        )
        if existing:
            candidate.imported_product_id = existing.id
            candidate.approval_status = "IMPORTED"
            candidate.imported_at = datetime.now(timezone.utc)
            candidate.import_result = "ALREADY_EXISTS"
            candidate.import_failure_reason = None
            self.db.commit()
            return self._dto(self._get(existing.id))

        product = self._build_candidate_product(candidate, snapshot, enrichment, commercial)
        self.db.add(product)
        self.db.flush()
        self._add_candidate_content(product, enrichment)
        self._add_candidate_images(product, snapshot.get("images", []))
        for position, variant_data in enumerate(prepared_variants, start=1):
            variant = self._build_candidate_variant(product, variant_data, position, commercial)
            product.variants.append(variant)
            self.db.flush()
            self._sync_variant_warehouse_inventory(
                product,
                variant,
                InventorySnapshot(
                    total_inventory=variant.total_inventory or 0,
                    cj_inventory=variant.cj_inventory or 0,
                    factory_inventory=variant.factory_inventory or 0,
                    verification_status=variant.verified_warehouse,
                    warehouses=self._candidate_warehouses(snapshot, variant.supplier_variant_id),
                ),
            )

        readiness = CatalogReadinessService.validate_activation(product)
        product.supplier_validation_details = {
            **(candidate.data_snapshot or {}).get("commercial_result", {}),
            "catalog_readiness": {
                "ready": readiness.ready,
                "blocking_reasons": list(readiness.blocking_reasons),
            },
            "enrichment": {
                "category": enrichment.get("category"),
                "subcategory": enrichment.get("subcategory"),
                "attributes": enrichment.get("attributes", {}),
                "seo_title": enrichment.get("seo_title"),
                "seo_meta_description": enrichment.get("seo_meta_description"),
                "search_keywords": enrichment.get("search_keywords", []),
            },
        }
        candidate.imported_product_id = product.id
        candidate.approval_status = "IMPORTED"
        candidate.imported_at = datetime.now(timezone.utc)
        candidate.import_result = "IMPORTED"
        candidate.import_failure_reason = None
        self.db.commit()
        return self._dto(self._get(product.id))

    @staticmethod
    def _prepare_candidate_variants(
        variants: list[object], commercial: dict
    ) -> list[dict]:
        prepared: list[dict] = []
        seen_ids: set[str] = set()
        for item in variants:
            if not isinstance(item, dict):
                raise BadRequestError("Invalid supplier variant data")
            variant_id = str(item.get("supplier_variant_id") or "").strip()
            variant_sku = str(item.get("supplier_variant_sku") or "").strip()
            if not variant_id or not variant_sku:
                raise BadRequestError("Supplier variant VID and SKU are required")
            if variant_id in seen_ids:
                raise BadRequestError("Duplicate supplier variant VID")
            seen_ids.add(variant_id)
            if item.get("selling_price_inr") is None and commercial.get("minimum_price_inr") is None:
                raise BadRequestError("Deterministic variant price is missing")
            prepared.append({**item, "supplier_variant_id": variant_id, "supplier_variant_sku": variant_sku})
        return prepared

    def _build_candidate_product(
        self, candidate: SupplierCandidate, snapshot: dict, enrichment: dict, commercial: dict
    ) -> Product:
        variants = snapshot["variants"]
        return Product(
            id=uuid4(),
            slug=self._unique_slug(enrichment["title"], candidate.supplier_product_id),
            name=enrichment["title"],
            description=enrichment["description"],
            status="DRAFT",
            supplier=candidate.supplier,
            supplier_product_id=candidate.supplier_product_id,
            supplier_source_url=(snapshot.get("reference_data") or {}).get("product_url"),
            category_id=self._category_id(enrichment.get("category")),
            supplier_cost=self._decimal_from_variant(variants[0], "supplier_cost_inr"),
            shipping_cost=self._decimal_from_freight(snapshot.get("freight", {})),
            selling_price=Decimal(str(commercial["minimum_price_inr"])),
            currency="INR",
            total_inventory=sum(int(item.get("total_inventory") or 0) for item in variants),
            cj_inventory=sum(int(item.get("cj_inventory") or 0) for item in variants),
            factory_inventory=sum(int(item.get("factory_inventory") or 0) for item in variants),
            verified_warehouse="verified" if snapshot.get("warehouses") else None,
            last_supplier_sync_at=datetime.now(timezone.utc),
            commercial_status="APPROVED",
            commercial_reasons=commercial.get("failure_reasons", []),
            supplier_validation_status=candidate.supplier_validation_status,
            supplier_validation_score=candidate.supplier_validation_score,
            supplier_validation_notes=[],
            supplier_validated_at=datetime.now(timezone.utc),
            approval_decided_at=candidate.decision_at,
            approval_decided_by_user_id=candidate.decision_by_user_id,
            approval_evidence={"source": "SUPPLIER_CANDIDATE_APPROVAL", "candidate_id": str(candidate.id)},
        )

    def _category_id(self, slug: str | None) -> int | None:
        if not slug:
            return None
        category = self.db.scalar(select(Category).where(Category.slug == slug))
        return category.id if category else None

    @staticmethod
    def _decimal_from_variant(variant: dict, key: str) -> Decimal | None:
        value = variant.get(key)
        return Decimal(str(value)) if value is not None else None

    @staticmethod
    def _decimal_from_freight(freight: object) -> Decimal | None:
        if not isinstance(freight, dict) or freight.get("cost_inr") is None:
            raise BadRequestError("Freight cost is missing")
        return Decimal(str(freight["cost_inr"]))

    @staticmethod
    def _build_candidate_variant(product: Product, item: dict, position: int, commercial: dict) -> ProductVariant:
        return ProductVariant(
            product_id=product.id,
            supplier_variant_id=item["supplier_variant_id"],
            supplier_variant_sku=item["supplier_variant_sku"],
            name=str(item.get("name") or ""),
            attributes=str(item.get("attributes") or ""),
            supplier_cost=AdminProductService._decimal_from_variant(item, "supplier_cost_inr"),
            supplier_cost_usd=AdminProductService._decimal_from_variant(item, "supplier_cost_usd"),
            selling_price=Decimal(str(item.get("selling_price_inr") or commercial["minimum_price_inr"])),
            total_inventory=int(item.get("total_inventory") or 0),
            cj_inventory=int(item.get("cj_inventory") or 0),
            factory_inventory=int(item.get("factory_inventory") or 0),
            verified_warehouse="verified",
            weight_grams=AdminProductService._decimal_from_variant(item, "weight_grams"),
            position=position,
        )

    @staticmethod
    def _candidate_warehouses(snapshot: dict, variant_id: str) -> list[WarehouseInventorySnapshot]:
        return [
            WarehouseInventorySnapshot(
                warehouse_country=str(item.get("warehouse_country") or ""),
                storage_id=item.get("storage_id"),
                warehouse_name=item.get("warehouse_name"),
                total_inventory=int(item.get("total_inventory") or 0),
                cj_inventory=int(item.get("cj_inventory") or 0),
                factory_inventory=int(item.get("factory_inventory") or 0),
                verification_status=item.get("verification_status"),
            )
            for item in snapshot.get("warehouses", [])
            if isinstance(item, dict) and item.get("supplier_variant_id") == variant_id
        ]

    def _add_candidate_content(self, product: Product, enrichment: dict) -> None:
        for position, feature in enumerate(enrichment.get("key_features", []), start=1):
            self.db.add(ProductFeature(product_id=product.id, value=feature, position=position))
        for position, (label, value) in enumerate(enrichment.get("attributes", {}).items(), start=1):
            self.db.add(ProductSpecification(product_id=product.id, label=str(label), value=str(value), position=position))
        for keyword in dict.fromkeys(enrichment.get("search_keywords", [])):
            self.db.add(ProductTag(product_id=product.id, value=keyword))

    def _add_candidate_images(self, product: Product, images: object) -> None:
        if not isinstance(images, list):
            return
        for position, image_url in enumerate(images, start=1):
            if isinstance(image_url, str) and image_url.strip():
                product.images.append(ProductImage(url=image_url.strip(), position=position))

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

        if (
            candidate is None
            or candidate.approval_status in {"REVIEW", "REJECTED"}
            or candidate.readiness_status == "REJECTED"
        ):
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
        if (candidate.data_snapshot or {}).get("enrichment", {}).get("status") != "ENRICHED":
            return BulkApprovedProductImportItem(
                requested_id=requested_id,
                status="REJECTED_NOT_APPROVED",
                canonical_supplier_product_id=candidate.supplier_product_id,
                product_id=None,
                message="Successful enrichment is required before import",
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
        refresh_readiness = payload.brand_id is not None
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
        if refresh_readiness:
            self._refresh_catalog_readiness(product)
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

    @staticmethod
    def _refresh_catalog_readiness(product: Product) -> None:
        readiness = CatalogReadinessService.validate_activation(product)
        details = dict(product.supplier_validation_details or {})
        details["catalog_readiness"] = {
            "ready": readiness.ready,
            "blocking_reasons": list(readiness.blocking_reasons),
        }
        product.supplier_validation_details = details

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
            for variant in sorted(product.variants, key=lambda item: item.position):
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
        stored_warehouses = list(self.db.scalars(
            select(SupplierVariantInventory)
            .where(
                SupplierVariantInventory.product_id == product.id,
                SupplierVariantInventory.variant_id == variant.id,
                SupplierVariantInventory.supplier_variant_id == variant.supplier_variant_id,
            )
            .order_by(SupplierVariantInventory.id)
        ))
        identities = set()
        used_stored_ids = set()
        for warehouse in snapshot.warehouses:
            stored = next(
                (
                    item for item in stored_warehouses
                    if item.id not in used_stored_ids
                    and item.warehouse_country == warehouse.warehouse_country
                    and (
                        (warehouse.storage_id and item.storage_id == warehouse.storage_id)
                        or (warehouse.warehouse_name and item.warehouse_name == warehouse.warehouse_name)
                        or (warehouse.storage_id is None and warehouse.warehouse_name is None)
                    )
                ),
                None,
            )
            if stored:
                used_stored_ids.add(stored.id)
            storage_id = warehouse.storage_id or (stored.storage_id if stored else None)
            warehouse_name = warehouse.warehouse_name or (stored.warehouse_name if stored else None)
            identity = (
                stored.warehouse_identity if stored and not warehouse.storage_id and not warehouse.warehouse_name
                else storage_id or f"{warehouse.warehouse_country}:{warehouse_name or ''}"
            )
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
            record.storage_id = storage_id
            record.warehouse_name = warehouse_name
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
            readiness_status=candidate.readiness_status or "REVIEW",
            supplier_validation_status=candidate.supplier_validation_status,
            supplier_validation_score=candidate.supplier_validation_score,
            commercial_status=candidate.commercial_status,
            market_status=candidate.market_status,
            discovery_min_selling_price_inr=candidate.discovery_min_selling_price_inr,
            discovery_max_selling_price_inr=candidate.discovery_max_selling_price_inr,
            snapshot_status=candidate.snapshot_status,
            main_image=snapshot.get("main_image"),
            variants=snapshot.get("variants", []),
            images=snapshot.get("images", []),
            reference_data=snapshot.get("reference_data", {}),
            warehouses=snapshot.get("warehouses", []),
            logistics=snapshot.get("logistics", {}),
            freight=snapshot.get("freight", {}),
            commercial_result=snapshot.get("commercial_result", {}),
            enrichment=snapshot.get("enrichment", {}),
            failure_reasons=snapshot.get("commercial_result", {}).get("failure_reasons", []),
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