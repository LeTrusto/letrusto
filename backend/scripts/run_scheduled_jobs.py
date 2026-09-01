from __future__ import annotations

import asyncio
import logging
import sys

from app.services.scheduled_job_service import run_scheduled_job


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def main() -> int:
    try:
        result = asyncio.run(run_scheduled_job())
    except Exception:
        logging.getLogger(__name__).exception("Scheduled maintenance job failed")
        return 1
    return 1 if result["status"] == "PARTIAL_FAILURE" else 0


if __name__ == "__main__":
    sys.exit(main())