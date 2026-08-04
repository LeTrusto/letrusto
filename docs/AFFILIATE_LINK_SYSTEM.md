# Affiliate Link System

## Overview

LeTrusto uses a product-level affiliate-link system so each product can resolve to an exact retailer landing page instead of a generic search result.

The current Amazon Associates store ID is:

```text
letrusto-21
```

## Architecture

| Layer | Responsibility |
| --- | --- |
| Database | Stores per-product affiliate fields such as `amazonAsin`, `amazonAffiliateUrl`, and `flipkartAffiliateUrl`. |
| Backend API | Exposes the fields in product DTOs and removes Amazon search links from API responses. |
| Frontend helper | Resolves the final Amazon URL in `frontend/lib/affiliate.ts`. |
| Buy button UI | Renders the Amazon button, disables it when unavailable, and tracks clicks. |
| Analytics | Emits a GA4 `affiliate_click` event for outbound affiliate taps. |

## URL Generation Rules

### Amazon

`frontend/lib/affiliate.ts` resolves the Amazon URL in this order:

1. Use `amazonAffiliateUrl` if present.
2. Otherwise use `amazonAsin` and build:

```text
https://www.amazon.in/dp/{ASIN}?tag=letrusto-21
```

3. If neither field exists, the Amazon button is disabled and shows `Currently unavailable`.

### Flipkart

Flipkart uses the stored `flipkartAffiliateUrl` when available. If it is missing, the current runtime behavior can still fall back to the existing retailer link entry for that product.

## How to Add a New Product

1. Add the product record in the backend seed data or admin workflow.
2. Set the Amazon fields when the exact product page is known:
   - `amazonAsin`
   - `amazonAffiliateUrl`
3. Set `flipkartAffiliateUrl` when a retailer-specific affiliate URL is available.
4. Re-run the database seed or update the product row through the product editor/admin workflow.
5. Verify the product page shows a direct Amazon product page, not a search page.

## How to Update an ASIN

If a product changes or a more accurate Amazon product page is found:

1. Update `amazonAsin` or `amazonAffiliateUrl` in the database.
2. Rebuild or refresh the frontend.
3. Confirm the resulting Amazon URL still includes `tag=letrusto-21`.

## Click Tracking

Amazon and retailer button clicks emit a GA4 event:

```ts
gtag("event", "affiliate_click", {
  retailer: "amazon",
  product_name: product.name,
  product_id: product.id,
  category: product.category,
  affiliate: "amazon",
});
```

The button component also keeps the existing backend click endpoint for product-link analytics.

## Validation Rules

- Amazon buttons must never point to a search URL.
- If no Amazon affiliate destination exists, the button must be disabled.
- All Amazon URLs must contain `tag=letrusto-21`.
- No duplicate GA4 page-view events should be introduced by affiliate tracking.

## Common Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Amazon button shows `Currently unavailable` | The product has no `amazonAsin` or `amazonAffiliateUrl`. | Populate one of the fields for that product. |
| Amazon opens a search result page | A stale old URL is still present in product data. | Replace it with `amazonAffiliateUrl` or an ASIN-based URL. |
| GA4 event missing | Script not loaded in production or GA blocked by browser settings. | Confirm production-only loading is active and test in a non-blocked browser profile. |
| Click endpoint not recording | Backend unavailable or affiliate link missing an ID. | Confirm the API is running and product buy links still carry IDs. |

## Current State

- Production-only GA4 loading is implemented with `next/script`.
- Product buy links now prefer direct affiliate product pages.
- Amazon search URLs have been removed from the source catalog and seed scripts.
