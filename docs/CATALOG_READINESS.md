# Catalog Readiness Foundation

This document describes the implemented readiness guardrails for the active Printful catalog. The CJ mapping and inventory references below are historical Phase 2 compatibility only.

## Source of truth

The production catalog source is the backend Product API backed by PostgreSQL. The storefront no longer falls back to legacy static product arrays.

## Category mapping

The initial LeTrusto taxonomy is configuration-backed in `app.core.catalog_readiness`:

- `jewellery`
- `hair-style`
- `beauty-tools`
- `accessories`
- `gifts`
- `home-kitchen`
- `fitness`
- `baby-care`
- `pet-care`

Historical CJ mapping priority was:

1. CJ category ID
2. CJ category path
3. Explicit product attributes
4. Manual review/override

The initial mapping tables are intentionally empty. Unknown products remain non-active.

## Brand policy

- Existing approved brands may be assigned.
- Explicit generic/unbranded products use `Generic / Unbranded` classification.
- Missing, inferred, new, or manufacturer-only brands require review.
- Arbitrary CJ text never creates a customer-facing Brand automatically.

## Activation gate

Supplier-backed products must have:

- supplier and supplier product ID
- name and description
- category and approved brand classification
- valid approved-host primary image
	- active variants with supplier IDs, SKUs, prices, and a valid active-supplier availability model
- shipping cost
- approved commercial review
- supplier validation approval
- inventory sync no older than 30 minutes

The gate is read-only until all checks pass; it never mutates existing records.

## Pricing readiness

`CatalogPricingPolicy` uses Decimal values and centralizes:

- FX rate
- payment fee
- RTO reserve
- target contribution margin
- tax treatment
- tax rate

Tax defaults to `UNREGISTERED_NO_GSTIN`. This means only that the business currently has no GSTIN configured. It does not mean legally exempt, zero-rated, or tax-free. No GST rate is invented and no GST amount is added or collected by the pricing system. CAC remains separate commercial-review data.

The existing launch pricing calculator remains compatible with existing tests and records; no current product prices were changed by this phase.

## Images

Approved external hosts are:

- `cf.cjdropshipping.com`
- `oss-cf.cjdropshipping.com`

URLs are stored as source references. No image download, proxy, or CDN migration is performed. Position `1` remains the primary image.

## Inventory

Printful POD availability is not converted into warehouse quantities. There is currently no active warehouse inventory source for Printful, and `CatalogInventorySyncService` reports `NOT_APPLICABLE_POD` without fabricating quantities. CJ sellable inventory remains available only for historical records and compatibility paths.

## Re-import policy

Supplier identity remains `supplier + supplier_product_id`. New products are DRAFT. Existing DRAFT products may synchronize source-owned fields. ACTIVE products require review for customer-facing or commercial changes. Products with order history are never deleted or recreated.
