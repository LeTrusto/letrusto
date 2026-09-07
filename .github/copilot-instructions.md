# LeTrusto Repository Instructions

## Source Of Truth

The repository is authoritative. Inspect current code, migrations, tests, and configuration before relying on chat history or stale documentation.

## Current Product Direction

LeTrusto is currently a B2B SaaS product for customer social-proof widgets and embeddable experiences.

Active product areas are:

- Account registration, authentication, and onboarding
- Widget creation and management
- Customer event management
- Public embed delivery and domain protection
- Plan entitlements and usage limits
- Admin analytics and operational visibility

Subscription and card-payment work is paused. Do not retry payment providers, change billing configuration, or modify billing code unless the user explicitly reopens that work.

Historical non-SaaS product work is out of scope. Do not propose, prioritize, restore, or mention it as active work unless the user explicitly asks for historical context.

## Architecture

Reuse existing implementations before creating new models, services, repositories, endpoints, utilities, adapters, API clients, hooks, or components. Follow the existing FastAPI, SQLAlchemy 2, Alembic, Next.js App Router, React, TypeScript, API-client, authentication, and test patterns.

Keep customer-facing SaaS work scoped to the task. Do not redesign unrelated frontend surfaces or create competing architectures.

## Database And Deployment Safety

- Never modify an existing Alembic migration; create a new additive migration for schema changes.
- Inspect foreign keys and cascade behavior before data deletion.
- Never delete users, admins, authentication records, or unrelated application data.
- Do not run destructive seed/reset scripts against the current database.
- Do not re-enable `seed_products.py`, `seed_smartphones.py`, `seed_hosting_saas.py`, or `sync_verified_apple_iphones.py` during normal startup.
- Do not modify Railway or Vercel configuration unless explicitly requested.
- Do not commit, push, merge, or deploy unless explicitly requested.

## Security

Never expose or log API keys, access tokens, refresh tokens, passwords, payment secrets, or authorization headers. Never bypass authentication. Do not create real payment transactions or customer records during development verification.

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

- Backend models: `backend/app/models/entities.py`
- Backend entry: `backend/app/main.py`
- Migrations: `backend/alembic/versions/`
- Entitlements: `backend/app/services/entitlement_service.py`
- Widget APIs: `backend/app/api/v1/endpoints/widgets.py`
- Public embed API: `backend/app/api/v1/endpoints/public_embed.py`
- Frontend API client: `frontend/services/api.ts`
- Frontend auth: `frontend/lib/authContext.tsx`

When documentation conflicts with code, verify the repository and update documentation only when the task requires it.
