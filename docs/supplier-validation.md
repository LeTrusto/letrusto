# LeTrusto — Supplier Validation Report

## CJ Dropshipping

| Field | Value |
|-------|-------|
| Supplier | CJ Dropshipping |
| Country | China (primary), US/UK/DE/FR/TH warehouses |
| Integration type | REST API (v2.0) |
| API documentation | https://developers.cjdropshipping.com/en/api/introduction.html |
| Authentication | API Key → Access Token (180-day life, 15-day token, refreshable) |

### Capabilities

| Capability | Status | Notes |
|-----------|--------|-------|
| Product data | ✅ Available | Product List V2, Product Details — full product info |
| SKU | ✅ Available | Product SKU (SPU) + Variant SKU |
| Variants | ✅ Available | Variant query by product ID, includes option keys, images |
| Inventory | ✅ Available | Per-variant, per-warehouse; verified vs unverified |
| Price | ✅ Available | Sell price in USD; variant-level pricing |
| Shipping to India | ⚠️ Requires testing | Freight Calculation endpoint accepts `endCountryCode=IN`; actual options/cost depend on product logistics properties |
| Estimated delivery | ⚠️ Partial | `deliveryCycle` field (processing days) + `logisticAging` (transit days) |
| Order API | ✅ Available | Shopping/Order endpoints (Section 5 in docs) — NOT validated in Phase 2 |
| Tracking | ✅ Available | Track by tracking number; returns carrier, status, last mile info |
| Returns information | ⚠️ Via dispute API | Section 7 — Dispute endpoints, not validated |
| Minimum order | UNKNOWN | `directMinOrderNum` field exists but rarely populated |
| Payment requirements | UNKNOWN | CJ account balance or payment setup required |
| Product categories | ✅ Available | 3-level category tree |
| Automation level | HIGH | Full API for products, orders, tracking |
| Videos | ✅ Available | Video query by product ID |

### Known Limitations

1. **Rate limits**: QPS=1 per endpoint; free/v1 users limited to 1000 requests/day
2. **Prices in USD**: All product/shipping prices returned in USD; INR conversion required
3. **India shipping**: Must validate per-product; not all CJ products have India shipping routes
4. **Inventory verification**: CJ distinguishes "verified" (CJ warehouse) vs "unverified" (factory) inventory
5. **Product images**: Hosted on CJ CDN — may need caching for production
6. **Category mapping**: CJ categories don't map 1:1 to LeTrusto categories; manual mapping needed
7. **Sandbox**: CJ provides sandbox environment for order testing (documented but not validated)

### Validation Status

**PARTIAL** — Product data and inventory retrieval confirmed via API documentation. Shipping to India and order flow require live API key testing.
