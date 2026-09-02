# LeTrusto Digital Product Commerce Boundary

## Current state

The Small Business Finance & Pricing Toolkit is a published preview page with a real workbook asset stored outside `frontend/public/`. Its price and purchase panel are intentionally marked as planned; the site does not accept payment or provide downloads.

Digital products do not use the physical cart, `Order`, shipping address, inventory reservation, Printful fulfillment, or physical checkout flow.

## Deferred architecture

Before launch, digital commerce needs a separate lifecycle:

`Digital Product -> Payment Attempt -> Server-Verified Payment -> Purchase/Entitlement -> Secure Download`

The minimum implementation still requires additive backend models and migrations for digital products or product references, payment attempts, verified purchases/entitlements, and download access records or signed, short-lived download authorization. It also requires dedicated Razorpay creation and server-side verification endpoints, authenticated ownership checks, replay and abuse controls, and clear payment failure and cancellation handling.

Those pieces are not present yet. Enabling a button against the physical order flow would risk shipping requirements, Printful fulfillment, and entitlement delivery failures. Checkout therefore remains disabled until the separate lifecycle can be implemented and tested end to end.

## Delivery requirements for the next milestone

- Keep paid files outside public web assets.
- Create an entitlement only after server-side verification of a successful payment.
- Require authenticated or otherwise securely controlled access to downloads.
- Avoid shipping addresses, physical inventory, and Printful calls.
- Make repeated verification and download requests idempotent and bounded.
- Preserve the existing physical Razorpay and Printful order behavior.
