from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import httpx
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import Product, ProductImage, ProductVariant
from app.schemas.admin_products import (
    AdminProductDTO,
    AdminProductListResponse,
    AdminProductVariantDTO,
    CommercialReviewResponse,
    PriceCalculationRequest,
    PriceCalculationResponse,
    ProductImportRequest,
    ProductStatusUpdate,
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

    async def import_product(self, payload: ProductImportRequest) -> AdminProductDTO:
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

        product = Product(
            id=uuid4(), slug=self._unique_slug(normalized.title, normalized.supplier_product_id), name=normalized.title,
            description=normalized.description or normalized.title, status="DRAFT", supplier=normalized.supplier_id,
            supplier_product_id=normalized.supplier_product_id,
            supplier_cost=Decimal(str(normalized.cost_inr)) if normalized.cost_inr is not None else None,
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
        self.db.commit()
        return self._dto(self._get(product.id))

    def update_status(self, product_id: UUID, payload: ProductStatusUpdate) -> AdminProductDTO:
        product = self._get(product_id)
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

    def _get(self, product_id: UUID) -> Product:
        stmt = select(Product).options(selectinload(Product.images), selectinload(Product.variants)).where(Product.id == product_id)
        product = self.db.scalars(stmt).unique().first()
        if not product:
            raise NotFoundError("Catalog product not found")
        return product

    def _unique_slug(self, title: str, supplier_product_id: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "supplier-product"
        return f"{base}-{supplier_product_id.lower()}"[:150]

    def _dto(self, product: Product) -> AdminProductDTO:
        return AdminProductDTO(
            id=product.id, slug=product.slug, name=product.name, description=product.description, status=product.status,
            supplier=product.supplier, supplier_product_id=product.supplier_product_id, supplier_source_url=product.supplier_source_url,
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