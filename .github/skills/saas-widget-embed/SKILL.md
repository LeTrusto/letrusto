---
name: saas-widget-embed
description: "Use when implementing or auditing LeTrusto SaaS widgets, customer events, public embeds, origin/domain protection, usage limits, or embed script behavior."
---

# SaaS Widget and Embed Workflow

1. Identify the owning endpoint/service and frontend surface:
   - `backend/app/api/v1/endpoints/widgets.py`
   - `backend/app/api/v1/endpoints/widget_events.py`
   - `backend/app/api/v1/endpoints/public_embed.py`
   - `backend/app/services/entitlement_service.py`
   - `frontend/services/saas.service.ts`
   - `frontend/public/widget.js`
2. Trace model/schema ownership in `backend/app/models/entities.py`.
3. Check authentication, widget ownership, active state, approved events, origin matching, cache headers, and monthly usage accounting.
4. Preserve response schemas and existing API-client patterns.
5. Add or update focused tests for success, unauthenticated, forbidden, wrong-origin, inactive-widget, limit-reached, and empty-event behavior.
6. Run focused backend tests, then frontend tests/lint if the client changed.

Never weaken domain protection, bypass ownership checks, or expose internal customer data through the public endpoint.
