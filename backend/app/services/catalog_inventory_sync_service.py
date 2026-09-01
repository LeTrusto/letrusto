import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Product
from app.services.admin_product_service import AdminProductService


logger = logging.getLogger(__name__)


class CatalogInventorySyncService:
    """Synchronize active CJ catalog products from authoritative inventory."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.products = AdminProductService(db)

    async def sync_active_products(self) -> dict[str, Any]:
        products = list(self.db.scalars(
            select(Product).where(Product.status == "ACTIVE", Product.supplier == "cj")
        ).all())
        synced = 0
        failed = 0
        failures: list[dict[str, str]] = []
        for product in products:
            try:
                await self.products.sync_inventory(product.id)
                synced += 1
            except Exception as exc:
                self.db.rollback()
                failed += 1
                category = type(exc).__name__
                failures.append({"product_id": str(product.id), "category": category})
                logger.warning(
                    "Catalog inventory sync failed",
                    extra={"supplier": "cj", "product_id": str(product.id), "error_category": category},
                )
        return {
            "supplier": "cj",
            "attempted": len(products),
            "synced": synced,
            "failed": failed,
            "failures": failures,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
