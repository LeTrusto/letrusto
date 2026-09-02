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

Cashfree, Stripe, supplier, OAuth, SMS, and AI variables remain required only when their corresponding existing flows are enabled. Do not enable a provider by partially configuring its credentials.

## Database and startup

Railway startup runs `alembic upgrade head`, initializes the production catalog, and then starts FastAPI. Current migration head is `20260902_39`, which adds isolated digital payment-attempt and entitlement tables. Verify the migration completes online against the Railway database before launch; the older offline-generation issue is intentionally unchanged.

## Payment verification

The digital product flow creates a server-side Razorpay order, checks the order amount/currency and payment relationship, verifies the signature and captured status, then creates the entitlement. The frontend must show success and enable download only after the verification response. The paid CSV stays outside `frontend/public/` and is served through an authenticated entitlement check.

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
