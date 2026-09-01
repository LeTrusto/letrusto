from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

class CatalogInventorySyncService:
    """Report that POD products have no warehouse inventory to synchronize."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def sync_active_products(self) -> dict[str, Any]:
        return {
            "supplier": "printful",
            "attempted": 0,
            "synced": 0,
            "failed": 0,
            "failures": [],
            "status": "NOT_APPLICABLE_POD",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
