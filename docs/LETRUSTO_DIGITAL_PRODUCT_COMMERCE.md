# LeTrusto Digital Product Commerce Boundary

## Current state

The published catalog currently contains two products with workbook assets stored outside `frontend/public/`: Small Business Finance & Pricing Toolkit (INR 499) and Freelancer Rate & Project Pricing Toolkit (INR 399). Authenticated customers pay through the dedicated Razorpay digital flow and download the selected asset after server verification.

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
- Add future products by defining one stable slug, price, and filename in both the frontend catalog and the backend `PRODUCTS` allowlist; never derive asset paths from request input.

## Conversion measurement

The consent-aware frontend records an allowlisted event sequence for the digital funnel: `digital_product_view`, `digital_product_auth_required`, `digital_product_checkout_started`, `digital_product_payment_initiated`, `digital_product_payment_failed`, `digital_product_payment_verified`, `digital_product_entitlement_created`, `digital_product_purchase_completed`, `digital_product_download_initiated`, and `digital_product_download_completed`. Product name and slug are the only product parameters; payment IDs, amounts, email addresses, and form contents are not sent to analytics. Purchase and entitlement events occur only after the backend verification response confirms an active entitlement.

## Next product decision

Do not add a third product until the current tool-to-product funnel has enough consented traffic to compare tool completion, product clicks, authentication drop-off, payment success, and downloads. The strongest next opportunity is a freelancer and agency client-work workbook connecting rate setting to project scope, quote review, invoice follow-up, and project profitability. It should be built only after the existing Freelancer Rate and Invoice workflows show demand; otherwise it would add catalog count without validated customer need.
