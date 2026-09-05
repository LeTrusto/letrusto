# B2B Social Proof SaaS Migration

**Status:** First migration task implemented  
**Date:** 2026-09-05

LeTrusto is being repositioned from physical commerce to a B2B Micro-SaaS platform for Social Proof and Review Widgets.

## What Changed

### Physical commerce is disabled by default

Physical commerce is safely archived rather than deleted:

- Existing physical tables and historical migrations remain in PostgreSQL for rollback and data retention.
- Existing physical API modules, supplier adapters, and fulfillment services remain in Git history/source for controlled archival.
- Physical catalog, cart/order, supplier discovery, supplier validation, and physical admin routers are not registered when the feature flag is false.
- Customer cart, checkout, physical order-detail, and physical order-history pages now show an explicit paused state.
- Scheduled inventory and order-reconciliation jobs return `SKIPPED_PHYSICAL_COMMERCE_DISABLED` without opening a database lock or running supplier work.
- Printful and CJ adapter construction raises a controlled error unless supplier integrations are explicitly enabled.

The controls are in `backend/app/core/config.py`:

```env
PHYSICAL_COMMERCE_ENABLED=false
SUPPLIER_INTEGRATIONS_ENABLED=false
```

Do not enable these flags for the new SaaS production deployment.

### New B2B SaaS database entities

The new additive migration is:

`backend/alembic/versions/20260905_41_b2b_social_proof.py`

It creates:

- `widgets`: widget ownership, customer domain, theme, position, delay, active state, and creation time.
- `widget_events`: social-proof/review events belonging to a widget, with approval, rating, review, customer, and display content fields.
- `subscriptions`: user plan, Razorpay subscription ID, status, current period end, and creation time.

All primary keys use PostgreSQL UUIDs, all owner foreign keys are indexed, and child rows cascade when their owning user/widget is deleted.

### SQLAlchemy models

The corresponding entities are in:

`backend/app/models/entities.py`

- `Widget`
- `WidgetEvent`
- `Subscription`

The `User` model now exposes `widgets` and `subscriptions` relationships. The entities are exported from `backend/app/models/__init__.py`.

## Step-by-Step Deployment Instructions

1. Review the migration and confirm the deployment environment points to the intended PostgreSQL database.
2. Confirm these production variables are set to false:

   ```env
   PHYSICAL_COMMERCE_ENABLED=false
   SUPPLIER_INTEGRATIONS_ENABLED=false
   ```

3. From the backend directory, apply the additive migration:

   ```powershell
   cd C:\Users\BasavannaS\Repos\letrusto\backend
   alembic upgrade head
   ```

4. Confirm the migration head:

   ```powershell
   alembic current
   alembic heads
   ```

   Expected head: `20260905_41`.

5. Deploy the backend to Railway and confirm startup completes migrations before Uvicorn starts.
6. Deploy the frontend to Vercel.
7. Confirm `/cart`, `/checkout`, `/orders/{id}`, and `/account/orders` show the paused state.
8. Confirm physical API paths are not registered while the feature flag is false.
9. Confirm authentication, registration, login, refresh, password reset, email verification, and Resend flows remain available.
10. Verify the Phase 2 widget slice below.

## Phase 2 Widget API and Embed Testing

Authenticated widget management uses the existing JWT bearer authentication:

- `POST /api/v1/widgets` creates a widget.
- `GET /api/v1/widgets` and `GET /api/v1/widgets/{id}` list/read only the current user's widgets.
- `PUT /api/v1/widgets/{id}` updates an owned widget.
- `DELETE /api/v1/widgets/{id}` deactivates an owned widget without deleting data.
- `POST /api/v1/widgets/{id}/events` creates an event.
- `GET /api/v1/widgets/{id}/events` lists events for an owned widget.
- `DELETE /api/v1/events/{id}` hides an owned event by setting `is_approved=false`.

The unauthenticated public response is:

```text
GET /api/v1/public/embed/{widget_id}
```

It returns only active widgets and approved events from the last 30 days, and includes `Access-Control-Allow-Origin: *`. The browser asset is served at `/widget.js`:

```html
<script src="https://letrusto.com/widget.js" data-id="WIDGET_UUID"></script>
```

For local testing, override the API base without rebuilding the frontend:

```html
<script src="http://localhost:3000/widget.js" data-id="WIDGET_UUID" data-api-base="http://localhost:8000"></script>
```

Focused local checks:

```powershell
cd C:\Users\BasavannaS\Repos\letrusto\backend
python -m compileall -q app/schemas/widgets.py app/api/v1/endpoints/widgets.py app/api/v1/endpoints/widget_events.py app/api/v1/endpoints/public_embed.py app/api/v1/api.py
cd ..
node --check frontend/public/widget.js
```

The script intentionally renders server content through DOM text nodes, rotates events after `display_delay`, and silently does nothing for empty, failed, or non-OK public responses.

## Validation Completed

- New models import successfully.
- New migration is the single Alembic head.
- Local database upgraded successfully to `20260905_41`.
- Frontend tests: `92 passed`.
- Frontend lint: passed.
- Frontend production build: passed.
- Retained authentication and digital-product tests: `28 passed`.
- Physical API route absence verified with `PHYSICAL_COMMERCE_ENABLED=false`.

The complete historical backend suite still contains tests for the retired physical-commerce and supplier behavior. Those tests require a follow-up test cleanup or archival pass as part of the broader strategy migration; they are not evidence that physical commerce remains enabled in the application.
