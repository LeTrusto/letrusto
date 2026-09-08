---
name: saas-release-readiness
description: "Use when preparing, auditing, or validating a LeTrusto B2B SaaS release involving auth, onboarding, widgets, embeds, entitlements, analytics, or production deployment."
---

# SaaS Release Readiness Workflow

1. Confirm the requested scope is active LeTrusto SaaS work. Stop and ask before payment, production data, deployment, or destructive actions.
2. Inspect `git status`, recent history, changed files, relevant routes/services/models, and nearby tests.
3. Validate backend with the narrowest relevant pytest selection, then `cd backend; pytest -q` when the slice is complete.
4. Validate frontend with focused Vitest coverage, then `npm run lint` and `npm run build` when frontend code changed.
5. Check auth boundaries, CORS/origin behavior, rate limits, entitlement enforcement, error states, migrations, and secret handling.
6. Separate verified facts from assumptions. Never call a production path verified without an observed result.
7. Finish with: changed behavior, validation commands/results, remaining risks, and explicit next action.

Do not use this workflow to revive historical non-SaaS work.
