# LeTrusto — Copilot Instructions

## Source of Truth

The repository code is the only source of truth. Never trust outdated chat memory or previous session summaries.

## Core Rules

1. **Never assume a feature exists.** Inspect the repository before referencing any file, route, component, or configuration.
2. **Inspect before modifying.** Read the target file and its dependencies before making changes.
3. **Preserve the current direction.** LeTrusto is an AI tools / software discovery, comparison, recommendation, guides, and affiliate monetization platform. Do not silently revert to an older product-marketplace direction.
4. **Avoid unnecessary rewrites.** Make the smallest safe change that satisfies the requirement.
5. **Reuse existing architecture.** Check `components/`, `lib/`, `services/`, `config/`, `types/`, and `hooks/` for existing implementations before creating new ones.
6. **Do not introduce duplicate systems.** One affiliate registry (`lib/softwareAffiliates.ts`), one homepage config (`config/homepage.ts`), one analytics tracker (`lib/analytics.ts`), one auth context (`lib/authContext.tsx`).
7. **Do not remove working functionality** without explicit user approval.
8. **Run validation after changes.** Frontend: `npm run lint` and `npm run build` from `frontend/`. Backend: `pytest -q` from `backend/`.
9. **Keep documentation synchronized.** After significant changes, update `docs/LETRUSTO_PROJECT_STATE.md`.
10. **When requirements are ambiguous**, inspect the repository first, then ask for clarification only if the code does not resolve the ambiguity.
11. **If something cannot be verified**, explicitly say so rather than guessing.

## Project References

- Project state: `docs/LETRUSTO_PROJECT_STATE.md`
- Affiliate tracker: `docs/LETRUSTO_AFFILIATE_TRACKER.md`
- AI tools taxonomy: `frontend/config/aiTools.ts`
- Homepage config: `frontend/config/homepage.ts`
- Software affiliate registry: `frontend/lib/softwareAffiliates.ts`
- Product affiliate helpers: `frontend/lib/affiliate.ts`
- API service layer: `frontend/services/api.ts`
- Backend entry: `backend/app/main.py`
- DB models: `backend/app/models/entities.py`
- Migrations: `backend/alembic/versions/`

## Coding Conventions

- Frontend: TypeScript strict, Next.js 16 App Router, Tailwind 4, server components by default, `"use client"` only when needed.
- Backend: Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2 settings, pg8000 driver.
- Affiliate links must come from the `SOFTWARE_AFFILIATES` registry or backend `affiliate_url` field — never hardcoded in page content.
- SEO metadata uses the `%s | LeTrusto` template from root layout; child pages set only the page-specific `title` string.
- Hydration-safe state: use lazy `useState` initializers or effects for localStorage reads; do not set state synchronously in effects.
