# Scheduled Maintenance Jobs

The backend does not start a scheduler inside the FastAPI web process. This avoids duplicate work when Railway runs more than one web replica.

Create a separate Railway service from the backend image with:

- Cron schedule: `*/15 * * * *`
- Start command: `python -m scripts.run_scheduled_jobs`
- The same `DATABASE_URL` and supplier/payment environment configuration as the backend service

The command performs one pass of the inventory-monitoring hook, operational alert evaluation, and the existing order lifecycle reconciliation. It exits after the pass so Railway can invoke it again on the next cron tick.

The job takes a PostgreSQL advisory lock using `SCHEDULED_JOB_LOCK_KEY` (default `826301`). Keep that value the same across scheduler instances. A concurrent invocation exits as `SKIPPED_OVERLAPPING` without touching inventory or orders.

Printful products remain POD-driven. There is currently no active warehouse inventory source, so the inventory-monitoring hook reports `NOT_APPLICABLE_POD` without calling CJ or fabricating Printful quantities. The scheduler does not create orders, payments, supplier orders, or customer records.

Alert configuration is backend-only:

- `LOW_STOCK_THRESHOLD` (default `5`): reserved for a future real warehouse inventory source; it does not apply to Printful POD today.
- `ALERT_EMAIL_COOLDOWN_MINUTES` (default `60`): suppresses repeated identical inventory-monitoring failures during the cooldown.

Alerts are sent to `SUPPORT_EMAIL` using the existing Resend configuration. Low-stock state recovers when stock rises above the threshold; sync-failure state recovers after a clean inventory pass. Email delivery failures are recorded in alert state and do not fail inventory synchronization or reconciliation.