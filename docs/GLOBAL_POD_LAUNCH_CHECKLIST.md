# Global POD Launch Checklist

This checklist separates repository work from actions that require LeTrusto owner approval, provider accounts, credentials, or legal acceptance.

## Owner Actions Required

- [x] Select Printful as the first POD provider.
- [ ] Create and verify the Printful merchant account.
- [ ] Generate the Printful API key and add it only to the backend deployment environment.
- [ ] Approve the provider product catalog, blank products, print areas, mockup style, and quality standards.
- [ ] Approve the countries and shipping destinations for launch.
- [ ] Approve production and delivery estimates shown to customers.
- [ ] Review and approve the made-to-order returns, damaged-item, replacement, and refund policy.
- [ ] Review tax, customs, duties, consumer protection, privacy, and business registration requirements for each launch market.
- [ ] Create or confirm the Stripe account for global payments.
- [ ] Add `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` to the backend deployment environment.
- [ ] Register the Stripe webhook endpoint:
  `https://letrusto.com/api/v1/payments/stripe/webhook`
- [ ] Add the Stripe webhook events used by the application: checkout completion, asynchronous payment success/failure, and checkout expiration.
- [ ] Confirm Razorpay production credentials and webhook configuration for India.
- [ ] Confirm production frontend and backend URLs for Stripe success and cancellation redirects.
- [ ] Run one controlled end-to-end payment and fulfillment test with test-mode credentials before enabling live payments.

## Completed Repository Work

- [x] Global POD storefront direction and public copy cleanup.
- [x] Legacy AI, affiliate, comparison, and old catalog public surfaces removed or redirected.
- [x] Imported unwanted household products have a precise production cleanup script.
- [x] Razorpay remains the India payment provider.
- [x] Stripe-hosted Checkout is implemented for non-India orders.
- [x] International orders are converted to USD using the configured server-side FX rate.
- [x] Stripe webhook signature verification and payment state handling are implemented.
- [x] Payment success consumes inventory reservations and hands eligible orders to fulfillment.
- [x] Frontend lint and production build pass.
- [x] Focused backend order, payment, and refund tests pass.

## Next Repository Work

- [x] Add the Printful adapter boundary using the existing supplier adapter protocol.
- [ ] Complete Printful catalog, mockup, and design-file integration.
- [ ] Add provider product search, product details, variants, mockups, inventory, and shipping-rate mapping.
- [ ] Add provider-specific catalog import and duplicate detection.
- [ ] Store supplier traceability and source image URLs for every imported item.
- [ ] Route fulfillment by product supplier without changing existing CJ validation semantics.
- [ ] Add provider tracking synchronization and webhook handling.
- [ ] Add admin controls for provider products, mockups, availability, and publish status.
- [ ] Add provider contract tests using mocked API responses only.
- [ ] Verify checkout currency, delivery estimates, and returns messaging against the approved launch markets.

## Safety Rules

- Do not paste API keys, webhook secrets, passwords, or payment credentials into chat or source files.
- Do not create live customer orders while validating integrations.
- Keep provider credentials backend-only.
- Do not enable live fulfillment until product quality, shipping, returns, tax, and payment behavior are approved.
