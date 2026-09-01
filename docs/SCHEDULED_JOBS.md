# Scheduled Maintenance Jobs

The backend does not start a scheduler inside the FastAPI web process. This avoids duplicate work when Railway runs more than one web replica.

Create a separate Railway service from the backend image with:

- Cron schedule: `*/15 * * * *`
- Start command: `python -m scripts.run_scheduled_jobs`
- The same `DATABASE_URL` and supplier/payment environment configuration as the backend service

The command performs one pass of active CJ inventory synchronization and the existing order lifecycle reconciliation. It exits after the pass so Railway can invoke it again on the next cron tick.

The job takes a PostgreSQL advisory lock using `SCHEDULED_JOB_LOCK_KEY` (default `826301`). Keep that value the same across scheduler instances. A concurrent invocation exits as `SKIPPED_OVERLAPPING` without touching inventory or orders.

Printful products are not selected by the catalog inventory sync. Printful remains POD-driven and is not routed through CJ warehouse inventory fields or reservations. The scheduler does not create orders, payments, supplier orders, or customer records.