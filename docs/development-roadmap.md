# LeTrusto Commerce Roadmap

> Current direction: Printful-only production commerce and controlled business scaling. CJ references in this document are historical Phase 2 compatibility unless explicitly marked otherwise.
> Status labels are intentional: COMPLETED, CURRENT GATE, NEXT, PRE-PUBLIC-LAUNCH, and PUBLIC LAUNCH.

The earlier brand, storefront, AI-platform, commerce-foundation, supplier-integration, checkout, and analytics work is preserved in repository history. This document is now the authoritative operating roadmap for the current commerce phase.

## COMPLETED

- Brand, storefront, authentication, and core commerce foundation.
- Product ingestion, normalization, review, pricing, economics, and admin approval workflow.
- Razorpay checkout and payment verification.
- Razorpay webhook handling.
- Historical CJ V2/V3 adapter foundation, supplier payment, and warehouse validation.
- Printful catalog, shipping, order, and tracking integration.
- Admin-only fulfillment preflight UI implementation, locally validated and awaiting deployment.

## CURRENT GATE

1. Deploy and smoke-test Admin Preflight UI.
2. Run and record production preflight.
3. Confirm product activation/readiness gates.
4. Confirm Razorpay payment gateway, webhook, order creation, reservation, and idempotency behavior.
5. Execute one controlled paid order with explicit rollback/refund plan.
6. Verify Printful order creation and shipment tracking in a non-production-safe test path.
7. Verify customer-facing order status.
8. Verify transactional email notification.
9. Verify logs, alerts, and failure visibility.

No controlled real customer transaction should occur until the production preflight gate passes.

## NEXT

11. Add operational monitoring, retries, and alerts.
12. Add customer tracking UI.
13. Add inventory refresh scheduler and stale-inventory protection.
14. Add low-stock and synchronization failure alerts.
15. Add admin fulfillment timeline and audit history.
16. Complete cancellation, returns, refunds, and support workflows.

## PRE-PUBLIC-LAUNCH

17. Complete shipping, delivery estimate, tax/GST, and legal review.
18. Review product quality/content for all launch products.
19. Complete SEO indexing and analytics/conversion tracking.
20. Complete transactional email testing.
21. Complete backup/restore and production monitoring checks.
22. Expand to 20–50 verified products.

## PUBLIC LAUNCH

23. Gradually open public ordering.
24. Monitor soft launch.
25. Complete full public launch.

## Historical Safety Record

The previous failed CJ order is not a successful fulfillment and must not be retried as an active order. See the current state document for the incident record and safety lesson.
