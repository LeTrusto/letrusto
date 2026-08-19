from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Product
from app.services.admin_product_service import AdminProductService


class CatalogInventorySyncService:
    """Reusable active-catalog sync primitive for a future scheduler.

    Scheduling is intentionally not started here because the repository has no
    existing scheduler framework. Callers can schedule this method later.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.products = AdminProductService(db)

    async def sync_active_products(self) -> dict[str, int | str]:
        products = list(self.db.scalars(
            select(Product).where(Product.status == "ACTIVE", Product.supplier == "cj")
        ).all())
        synced = 0
        failed = 0
        for product in products:
            try:
                await self.products.sync_inventory(product.id)
                synced += 1
            except Exception:
                failed += 1
        return {"synced": synced, "failed": failed, "completed_at": datetime.now(timezone.utc).isoformat()}
