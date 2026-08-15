from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import Product, ProductImage, ProductVariant
from app.schemas.admin_products import AdminProductDTO, AdminProductListResponse, AdminProductVariantDTO, ProductImportRequest, ProductStatusUpdate
from app.suppliers.economics import EconomicsConfig, calculate_economics
from app.suppliers.factory import build_supplier_adapter
from app.suppliers.normalizer import normalize_product


class AdminProductService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_products(self, status: str | None, supplier: str | None, include_legacy: bool, skip: int, limit: int) -> AdminProductListResponse:
        stmt = select(Product).options(selectinload(Product.images), selectinload(Product.variants)).order_by(Product.created_at.desc())
        count_stmt = select(func.count(Product.id))
        if supplier:
            stmt = stmt.where(Product.supplier == supplier)
            count_stmt = count_stmt.where(Product.supplier == supplier)
        elif include_legacy:
            stmt = stmt.where(Product.supplier.is_(None))
            count_stmt = count_stmt.where(Product.supplier.is_(None))
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
            images=[image.url for image in sorted(product.images, key=lambda item: item.position)],
            variants=[AdminProductVariantDTO(
                id=variant.id, supplier_variant_id=variant.supplier_variant_id, supplier_variant_sku=variant.supplier_variant_sku,
                name=variant.name, attributes=variant.attributes, supplier_cost=variant.supplier_cost,
                total_inventory=variant.total_inventory, cj_inventory=variant.cj_inventory, factory_inventory=variant.factory_inventory,
                verified_warehouse=variant.verified_warehouse, weight_grams=variant.weight_grams, active=variant.active, position=variant.position,
            ) for variant in sorted(product.variants, key=lambda item: item.position)],
        )