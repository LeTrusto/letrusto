from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import monotonic
from typing import Any, Callable

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.session import SessionLocal, engine
from app.services.catalog_inventory_sync_service import CatalogInventorySyncService
from app.services.order_reconciliation_service import OrderLifecycleReconciliationService


logger = logging.getLogger(__name__)


class ScheduledJobRunner:
    """Run one maintenance pass from a singleton external cron invocation."""

    def __init__(
        self,
        *,
        db_engine: Any = engine,
        db_session_factory: Callable[..., Session] = SessionLocal,
        lock_key: int | None = None,
    ) -> None:
        self.db_engine = db_engine
        self.db_session_factory = db_session_factory
        self.lock_key = lock_key if lock_key is not None else get_settings().SCHEDULED_JOB_LOCK_KEY

    async def run_once(self) -> dict[str, Any]:
        started_at = datetime.now(timezone.utc)
        started_clock = monotonic()
        job_name = "inventory_and_order_reconciliation"
        logger.info("Scheduled job started", extra={"job_name": job_name, "started_at": started_at.isoformat()})

        with self.db_engine.connect() as connection:
            acquired = bool(connection.execute(
                text("SELECT pg_try_advisory_lock(:lock_key)"),
                {"lock_key": self.lock_key},
            ).scalar())
            if not acquired:
                logger.info("Scheduled job skipped because another run holds the lock", extra={"job_name": job_name})
                return {
                    "job_name": job_name,
                    "status": "SKIPPED_OVERLAPPING",
                    "started_at": started_at.isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }

            with self.db_session_factory(bind=connection) as db:
                try:
                    inventory = await CatalogInventorySyncService(db).sync_active_products()
                    reconciliation = await OrderLifecycleReconciliationService(db).run_order_lifecycle_reconciliation()
                    result = {
                        "job_name": job_name,
                        "status": "SUCCEEDED" if not reconciliation.failures and not inventory["failed"] else "PARTIAL_FAILURE",
                        "started_at": started_at.isoformat(),
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                        "duration_seconds": round(monotonic() - started_clock, 3),
                        "inventory": inventory,
                        "reconciliation": reconciliation.model_dump(mode="json"),
                    }
                    logger.info(
                        "Scheduled job completed",
                        extra={
                            "job_name": job_name,
                            "status": result["status"],
                            "duration_seconds": result["duration_seconds"],
                            "inventory_attempted": inventory["attempted"],
                            "inventory_failed": inventory["failed"],
                            "reconciliation_failures": len(reconciliation.failures),
                        },
                    )
                    return result
                except Exception:
                    db.rollback()
                    logger.exception("Scheduled job failed", extra={"job_name": job_name})
                    raise


async def run_scheduled_job() -> dict[str, Any]:
    return await ScheduledJobRunner().run_once()