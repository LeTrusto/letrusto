# LeTrusto Repository Instructions

## Source Of Truth

The repository is authoritative. Inspect current code, migrations, tests, and configuration before relying on chat history or stale documentation.

## Current Product Direction

LeTrusto is an Indian ecommerce and CJ dropshipping platform.

Business progression:

Discover -> Curate -> Distribute -> Optimize -> Negotiate -> Exclusivity -> Private Label -> LeTrusto Brand

Roadmap:

- Phase 0: business validation, complete
- Phase 1: brand, complete
- Phase 2: supplier/product economics validation, complete
- Phase 3: production commerce backend, current
- Phase 4: admin/operations, later
- Phase 5: launch, later

The old mobile/affiliate catalog has been removed. Do not recreate or reseed it. The product database is expected to start at zero products until real CJ products are imported.

## Phase 2 Invariants

The existing Phase 2 supplier validation flow must remain intact. It supports real CJ search, product details, India shipping validation, economics, contribution, inventory distinction, scoring, and review classification.

Use the existing `backend/app/suppliers/adapters/cj_adapter.py` and existing normalization logic. Do not create a second CJ client or authentication flow.

Inventory semantics are fixed:

- `cjInventoryNum` is sellable inventory and the normal scoring input.
- `factoryInventoryNum` is factory supply, not normal sellable inventory.
- Never merge factory inventory into sellable inventory.

Do not change Phase 2 scoring thresholds, scoring weights, RTO/margin logic, supplier reliability rules, CJ authentication, or inventory mapping without explicit approval.

## Phase 3.1 Catalog

Current admin catalog APIs:

- `POST /api/v1/admin/products/import`
- `GET /api/v1/admin/products`
- `GET /api/v1/admin/products/{id}`
- `PATCH /api/v1/admin/products/{id}`

All admin catalog operations use the existing `get_current_admin` dependency. Imported CJ products start as `DRAFT`; supported statuses are `DRAFT`, `ACTIVE`, and `PAUSED`.

Preserve supplier traceability: supplier, supplier product ID, CJ variant IDs, supplier SKUs, source image URLs, supplier cost, shipping cost, total/CJ/factory inventory, verification status, and sync timestamps. Duplicate imports are identified by `supplier + supplier_product_id`.

## Architecture

Reuse existing implementations before creating new models, services, repositories, endpoints, utilities, adapters, API clients, hooks, or components. Follow the existing FastAPI, SQLAlchemy 2, Alembic, Next.js App Router, React, TypeScript, API-client, authentication, and test patterns.

Keep customer-facing mock/catalog migration scoped to the task. Do not redesign unrelated frontend surfaces or create competing catalog architectures.

## Database And Deployment Safety

- Never modify an existing Alembic migration; create a new additive migration for schema changes.
- Inspect foreign keys and cascade behavior before data deletion.
- Never delete users, admins, authentication records, CJ credentials, or unrelated application data during catalog work.
- Do not run destructive seed/reset scripts against the current database.
- Do not re-enable `seed_products.py`, `seed_smartphones.py`, `seed_hosting_saas.py`, or `sync_verified_apple_iphones.py` during normal startup.
- Do not modify Railway or Vercel configuration unless explicitly requested.
- Do not commit, push, merge, or deploy unless explicitly requested.

## Security

CJ communication remains backend-only. Never expose or log CJ API keys, access tokens, refresh tokens, passwords, or authorization headers. Never bypass authentication. Do not create real CJ orders, payments, or customer records during development verification.

## Workflow

1. Inspect the relevant owning code and nearby tests.
2. Search for reusable implementations before adding anything.
3. Make the smallest safe change requested.
4. Run focused validation immediately after editing.
5. Run milestone validation when requested or when the slice is complete.
6. Stop and ask before dangerous ambiguity involving deletion, authentication, payments, orders, or production deployment.

Standard commands:

- Backend: `pytest -q` from `backend/`
- Frontend: `npm run lint` and `npm run build` from `frontend/`

## Documentation References

- Project state: `docs/LETRUSTO_PROJECT_STATE.md`
- Backend models: `backend/app/models/entities.py`
- Backend entry: `backend/app/main.py`
- Migrations: `backend/alembic/versions/`
- CJ adapter: `backend/app/suppliers/adapters/cj_adapter.py`
- Frontend API client: `frontend/services/api.ts`
- Frontend auth: `frontend/lib/authContext.tsx`

When documentation conflicts with code, verify the repository and update documentation only when the task requires it.
