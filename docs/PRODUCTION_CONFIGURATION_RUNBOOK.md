# LeTrusto Production Configuration Runbook

Use deployment-provider environment settings for all production values. Do not put secrets in source control, Vercel client bundles, or documentation.

## Frontend / Vercel

| Variable | Required | Secret | Purpose and validation |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Yes | No | Public FastAPI origin. Set to the HTTPS Railway backend URL; the client appends `/api/v1`. |
| `NEXT_PUBLIC_APP_URL` | Yes | No | Canonical site origin used for metadata. Set to `https://letrusto.com`. |

The GA4 measurement ID is currently configured in the frontend analytics module. Analytics is sent only after explicit consent. No payment credentials belong in Vercel environment variables.

## Backend / Railway

| Variable | Required | Secret | Purpose and validation |
| --- | --- | --- | --- |
| `APP_ENV` | Yes | No | Set to `production`; enables production validation, rate limits, HSTS, and disables API docs. |
| `DATABASE_URL` | Yes | Yes | Railway PostgreSQL connection URL. Must not resolve to localhost in production. |
| `JWT_SECRET_KEY` | Yes | Yes | At least 32 random characters; never use the development placeholder. |
| `JWT_ALGORITHM` | Yes | No | Keep aligned with token verification; current value is `HS256`. |
| `CORS_ORIGINS` | Yes | No | Comma-separated HTTPS frontend origins, such as the canonical and approved Vercel domains. Production rejects wildcard and HTTP origins. |
| `PUBLIC_APP_URL` | Yes | No | HTTPS public site URL used in email links and customer-facing URLs. |
| `RESEND_API_KEY` | Yes | Yes | Server-side Resend API key for verification, reset, support, and customer email. |
| `FROM_EMAIL` | Yes | No | Verified Resend sender address on the configured domain. |
| `SUPPORT_EMAIL` | Yes | No | Customer support and operational notification recipient. |
| `RAZORPAY_ENV` | Yes for digital checkout | No | Set explicitly to `production` for live payments; use `sandbox` only for testing. |
| `RAZORPAY_KEY_ID` | Yes for digital checkout | No | Razorpay public identifier returned to the authenticated checkout client. Use the matching environment. |
| `RAZORPAY_KEY_SECRET` | Yes for digital checkout | Yes | Server-only secret used for order/payment verification. Never expose it client-side. |
| `RAZORPAY_WEBHOOK_SECRET` | Yes when Razorpay credentials are configured | Yes | Secret used for Razorpay webhook verification. |
| `RAZORPAY_STARTER_PLAN_ID` | Yes for paid SaaS subscriptions | No | Razorpay monthly plan ID for the Starter plan at ₹999; keep the value in Railway variables. |
| `RAZORPAY_PRO_PLAN_ID` | Yes for paid SaaS subscriptions | No | Razorpay monthly plan ID for the Pro plan at ₹2,499; keep the value in Railway variables. |
| `PHYSICAL_COMMERCE_ENABLED` | Yes | No | Keep `false`; physical catalog, checkout, supplier, and fulfillment routers remain archived. |
| `SUPPLIER_INTEGRATIONS_ENABLED` | Yes | No | Keep `false`; SaaS production must not construct supplier integrations. |

For the Phase 4 SaaS deployment, the relevant Railway values are:

```env
APP_ENV=production
CORS_ORIGINS=https://letrusto.com,https://www.letrusto.com,https://letrusto.vercel.app
PHYSICAL_COMMERCE_ENABLED=false
SUPPLIER_INTEGRATIONS_ENABLED=false
RAZORPAY_ENV=production
RAZORPAY_KEY_ID=rzp_live_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_STARTER_PLAN_ID=plan_...
RAZORPAY_PRO_PLAN_ID=plan_...
RAZORPAY_WEBHOOK_SECRET=...
```

Keep the Razorpay secret, plan IDs, and webhook secret in Railway only. Vercel needs only the public API configuration:

```env
NEXT_PUBLIC_API_BASE_URL=https://YOUR_RAILWAY_BACKEND_HOST
NEXT_PUBLIC_APP_URL=https://letrusto.com
```

The public embed endpoint is intentionally separate from application CORS. `GET /api/v1/public/embed/{widget_id}` returns `Access-Control-Allow-Origin: *` for external customer sites, while the global middleware continues to allow only the configured HTTPS application origins for authenticated traffic. `/widget.js` is served with `Cache-Control: public, max-age=3600, s-maxage=86400`.

Cashfree, Stripe, supplier, OAuth, SMS, and AI variables remain required only when their corresponding existing flows are enabled. Do not enable a provider by partially configuring its credentials.

## Database and startup

Railway startup runs `alembic upgrade head`, initializes the production catalog, and then starts FastAPI. Current migration head is `20260905_41`, which adds the B2B social-proof widget and event tables. Verify the migration completes online against the Railway database before launch; the older offline-generation issue is intentionally unchanged.

## Payment verification

The digital product flow creates a server-side Razorpay order, checks the selected product's allowlisted amount/currency and payment relationship, verifies the signature and captured status, then creates the entitlement. The frontend must show success and enable download only after the verification response. All paid CSV workbooks stay outside `frontend/public/` and are served through an authenticated entitlement check.

For sandbox testing, configure `RAZORPAY_ENV=sandbox`, matching test key ID/secret, and webhook secret in Railway or a local ignored `.env`. Perform one controlled purchase and confirm verification, entitlement, protected download, and download audit fields. Never use fabricated payment IDs or signatures.

## Email verification after Resend setup

1. Confirm the Resend key is present only in Railway and the sender domain is verified.
2. Register a test account and confirm the verification email link uses `PUBLIC_APP_URL`.
3. Exercise password reset and confirm its link and expiry behavior.
4. Submit a support ticket and service enquiry; confirm the customer confirmation and admin notification arrive.
5. Check provider logs and application logs for delivery failures without exposing API keys, tokens, or message contents.

## Launch security checks

- Rotate any credential that has been shared or exposed during development.
- Keep `.env` files ignored and untracked.
- Confirm the production frontend has no server secrets in its generated bundle.
- Confirm `CORS_ORIGINS` contains only intended HTTPS origins.
- Confirm no paid asset is under `frontend/public/`.
- Confirm physical Razorpay, cart, order, shipping, inventory, and Printful flows remain separate from digital commerce.

## Final launch checklist

Complete this checklist against the production providers; keep values in provider secret stores and deployment settings only.

### Code verified

- FastAPI startup runs database migrations, catalog initialization, and Uvicorn in that order.
- Current Alembic head is `20260905_41`; the deployed migration remains additive and must not be rewritten for offline generation.
- Production validation rejects localhost databases, placeholder JWT secrets, non-HTTPS public URLs, invalid CORS origins, mismatched payment environments, and incomplete configured Razorpay webhook settings.
- Digital payments verify the allowlisted product, provider order, amount, currency, captured status, signature, user ownership, and replay state before creating an entitlement.
- Digital downloads require an entitlement, increment download audit fields, and serve files from outside `frontend/public/`.
- Resend uses `FROM_EMAIL` as sender and `SUPPORT_EMAIL` as reply-to/operational recipient; delivery errors are logged without exposing message contents or credentials.
- Frontend analytics is production-only, consent-aware, allowlisted, and excludes payment IDs, email addresses, form contents, and secrets.
- The public funnel has eight tools, three digital products, nine services, canonical metadata, sitemap/robots handling, and preserved physical commerce routes.

### External operation required

- Railway: set and verify production `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, `PUBLIC_APP_URL`, Resend values, and matching Razorpay production values in the provider secret store.
- Vercel: set `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_APP_URL`; keep backend secrets out of Vercel client-visible configuration.
- Database: confirm PostgreSQL connectivity and run `alembic upgrade head` online, verifying migration `20260905_41` before traffic is enabled.
- Razorpay: verify the production account, webhook secret, webhook endpoint, and one approved sandbox transaction before live payments. Do not fabricate payment results.
- Resend: verify the sender domain/DNS and test verification, password reset, support, and service enquiry delivery without sending unnecessary customer data.
- GA4: verify the measurement ID, consent banner, and a consented event in the production property.
- Launch operations: rotate any credential previously exposed during development and review provider/application logs after deployment.

- [ ] Railway: set `APP_ENV=production`, the Railway `DATABASE_URL`, a rotated 32+ character `JWT_SECRET_KEY`, `JWT_ALGORITHM=HS256`, exact HTTPS `CORS_ORIGINS`, and `PUBLIC_APP_URL`.
- [ ] Railway: set `RESEND_API_KEY`, verified-domain `FROM_EMAIL`, and `SUPPORT_EMAIL`; confirm the sender domain and DNS are verified in Resend.
- [ ] Railway: set matching production Razorpay `RAZORPAY_ENV`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_STARTER_PLAN_ID`, `RAZORPAY_PRO_PLAN_ID`, and `RAZORPAY_WEBHOOK_SECRET`; keep all values server-side.
- [ ] Railway: explicitly set `PHYSICAL_COMMERCE_ENABLED=false` and `SUPPLIER_INTEGRATIONS_ENABLED=false`.
- [ ] Vercel: set `NEXT_PUBLIC_API_BASE_URL` to the HTTPS Railway origin and `NEXT_PUBLIC_APP_URL` to the canonical HTTPS site origin; do not add backend secrets.
- [ ] Database: confirm PostgreSQL connectivity, run `alembic upgrade head`, and verify migration `20260905_41` completes before application traffic is enabled.
- [ ] URLs and CORS: verify the deployed app calls the deployed API, the API allows only intended HTTPS frontend origins, and no wildcard or localhost origin is present.
- [ ] GA4: confirm measurement ID configuration, production consent banner behavior, and a consented test event without collecting payment IDs, emails, secrets, or form contents.
- [ ] Email: test verification, password reset, support, and service enquiry messages using `PUBLIC_APP_URL`; inspect provider logs without exposing tokens or message contents.
- [ ] Payment: with Razorpay sandbox credentials only, complete one digital-product order and verify order creation, payment verification, entitlement, and authenticated download. With production credentials, perform a small real transaction only through the approved launch process.
- [ ] Post-deployment: check public tools, all three digital products, services, quote form, authentication, legal pages, and Minku & Dinku; then review application/provider errors and rotate any credential that was exposed during development.
