from __future__ import annotations

import asyncio
import logging
import sys

from app.services.scheduled_job_service import run_scheduled_job
from app.core.config import get_settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def main() -> int:
    if not get_settings().PHYSICAL_COMMERCE_ENABLED:
        logging.getLogger(__name__).info("Physical commerce is disabled; scheduled commerce jobs skipped")
        return 0
    try:
        result = asyncio.run(run_scheduled_job())
    except Exception:
        logging.getLogger(__name__).exception("Scheduled maintenance job failed")
        return 1
    return 1 if result["status"] == "PARTIAL_FAILURE" else 0


if __name__ == "__main__":
    sys.exit(main())