# LeTrusto Current Project State

> Last updated: 2026-08-21
> Current phase: production commerce and controlled business scaling.

## Status Vocabulary

- **VERIFIED**: observed in the relevant deployed environment or validated test run.
- **EXPECTED**: the intended result, not yet observed.
- **NOT YET VERIFIED**: implemented or available, but the required verification has not occurred.
- **BLOCKED**: cannot proceed until the named gate is completed.

## Production

- Railway backend: **VERIFIED online**.
- PostgreSQL: **VERIFIED online**.
- Alembic revision: **VERIFIED `20260821_27`**.
- Razorpay LIVE: **VERIFIED configured**.
- CJ authentication: **VERIFIED**.
- CJ inventory and freight: **VERIFIED working**.
- Admin Preflight UI: **NOT YET VERIFIED in production**; implemented locally and awaiting deployment.

The latest production commits include:

- `7efcd02` — CJ fulfillment and supplier payment foundation
- `9cfab94` — preserve CJ warehouse identity
- `53300f8` — persist CJ warehouse inventory snapshots

The Admin Preflight UI implementation is in the repository but is not yet a production deployment fact.

## CJ Product 1 Candidate

| Field | Value | Status |
|---|---|---|
| Product | `bdf6c96b-9164-494f-8035-94b52bf4b7f1` | VERIFIED |
| Internal variant | `40bfc1bb-7768-4928-8517-7e58e22e811f` | VERIFIED |
| CJ VID | `E821D001-A0D1-41C3-B492-244A482BD63E` | VERIFIED |
| SKU | `CJJJCFCF00399-Black 90cm` | VERIFIED |
| Warehouse | China Warehouse | VERIFIED |
| Storage ID | `1` | VERIFIED |
| Country | `CN` | VERIFIED |
| CJ sellable inventory | `4` | VERIFIED |
| Factory inventory | `53963` | VERIFIED |
| India freight | Available | VERIFIED |
| Logistics | CJPacket Eub | VERIFIED from live CJ evidence |
| Freight | `$3.58` | VERIFIED from live CJ evidence |
| Delivery | `12–50 days` | VERIFIED from live CJ evidence |

CJ inventory and India freight are verified; LeTrusto production preflight remains the current gate.

The exact LeTrusto production preflight has **NOT YET BEEN VERIFIED** through the new Admin Preflight UI because that UI has not yet been deployed. Do not state that Product 1 is production `FULFILLABLE`.

## Current Blocker

**CURRENT TASK: Deploy Admin Preflight UI.**

After deployment, run the production preflight for internal variant `40bfc1bb-7768-4928-8517-7e58e22e811f` with:

- Quantity: `1`
- Destination: `IN`

Expected result: **FULFILLABLE**. This is EXPECTED, not VERIFIED, until returned by the deployed UI.

## Critical Safety

No controlled real customer transaction should occur until the production preflight gate passes.

Historical incident: `LT-20260821-700F9C89`

- Razorpay payment was captured.
- The LeTrusto order became `PAID`.
- CJ legacy order creation failed.
- No CJ supplier order was confirmed.
- Later investigation showed an incompatible legacy/incomplete CJ contract.
- No retry was performed.

This is a historical safety lesson, not an active order to retry. It must not be described as successful fulfillment.

## Test Status

- Backend: **VERIFIED 466 passed**.
- Frontend: **VERIFIED 8 passed** for the current Admin Preflight UI work.
- Known unrelated blocker, if still applicable: `tests/test_ai_tool_provenance_catalog.py` may fail with `ModuleNotFoundError: scripts`. Do not silently remove or relabel this warning without revalidation.

## Historical Architecture Context

LeTrusto retains earlier AI/software discovery, affiliate, storefront, and content systems in the repository. They are historical or supporting surfaces; the current business roadmap is governed by the production CJ commerce sequence in [development-roadmap.md](development-roadmap.md).
