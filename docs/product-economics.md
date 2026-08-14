# LeTrusto — Product Economics Report

## Economics Model

```
Supplier cost (USD → INR)
+ Shipping to India (USD → INR)
+ Payment gateway fee (~2.5%)
+ RTO/return reserve (UNKNOWN — needs data)
+ Creator commission (~10%)
+ Marketing allowance (~5%)
= Estimated variable cost

Selling price (target 2.5x markup, rounded to ₹49/₹99 price point)
- Estimated variable cost
= Estimated contribution
```

## Assumptions & Status

| Cost Line | Rate | Status |
|----------|------|--------|
| Supplier cost | From CJ API `sellPrice` (USD) | KNOWN (when API returns data) |
| USD → INR rate | 83.5 | ESTIMATED — use live rate in production |
| Shipping to India | CJ Freight Calculate API | KNOWN per-product (when available) |
| Payment fee | 2.5% of selling price | ESTIMATED (Razorpay-class) |
| RTO/return reserve | UNKNOWN | UNKNOWN — no historical return data |
| Creator commission | 10% of selling price | ESTIMATED (configurable) |
| Marketing allowance | 5% of selling price | ESTIMATED (blended target) |

## Sample Products (Template)

> No real product economics below until live CJ API validation is completed.
> Products listed here are templates showing the format.

### Template: Pearl Hair Clip Set

| Line | Amount | Status |
|------|--------|--------|
| Supplier cost | ₹___ | UNKNOWN |
| Shipping | ₹___ | UNKNOWN |
| Payment (2.5%) | ₹___ | ESTIMATED |
| RTO reserve | ₹___ | UNKNOWN |
| Creator (10%) | ₹___ | ESTIMATED |
| Marketing (5%) | ₹___ | ESTIMATED |
| **Selling price** | ₹299 | TARGET |
| **Contribution** | ₹___ | UNKNOWN |
| **Status** | NEEDS VALIDATION | |

## Pricing Strategy

- Target markup: 2.5x over supplier cost
- Selling prices rounded to ₹49/₹99 price points (₹149, ₹199, ₹249, ₹299, ₹399, ₹449, ₹499, etc.)
- Products below minimum contribution threshold should not be promoted
- Contribution % target: ≥20% (PROFITABLE), 5-20% (MARGINAL), <5% (UNPROFITABLE)

## Important Notes

1. **Do NOT claim profitability** until all material cost inputs are verified from live supplier data.
2. **RTO reserve** cannot be estimated until we have actual return rate data from operations.
3. **USD/INR rate** is volatile — use live rates in production and build in currency buffer.
4. **Shipping costs vary** significantly by product weight, dimensions, and logistics properties.
5. **Payment fees** may vary by gateway and payment method (UPI vs cards vs COD).
