# LeTrusto Digital Product Commerce Boundary

## Current state

The Small Business Finance & Pricing Toolkit is a published page with a workbook asset stored outside `frontend/public/`. Authenticated customers can pay INR 499 through the dedicated Razorpay digital flow and download the asset after server verification.

Digital products do not use the physical cart, `Order`, shipping address, inventory reservation, Printful fulfillment, or physical checkout flow.

## Separate lifecycle

`Digital Product -> Payment Attempt -> Server-Verified Payment -> Purchase/Entitlement -> Secure Download`

The implementation uses additive `digital_payment_attempts` and `digital_entitlements` tables, dedicated Razorpay creation and verification endpoints, authenticated ownership checks, replay-safe verification, and backend-private file serving. A verified payment creates one entitlement per user and product; downloads increment an audit count and never expose the filesystem path.

## Delivery requirements for the next milestone

- Keep paid files outside public web assets.
- Create an entitlement only after server-side verification of a successful payment.
- Require authenticated or otherwise securely controlled access to downloads.
- Avoid shipping addresses, physical inventory, and Printful calls.
- Make repeated verification and download requests idempotent and auditable.
- Preserve the existing physical Razorpay and Printful order behavior.
