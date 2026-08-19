# LeTrusto Trust Score v1

The Trust Score measures the strength and freshness of currently verified product information. It does not measure product quality, safety, popularity, sales, price, supplier performance, customer outcomes, or marketing performance.

## Formula

```text
Trust Score = Evidence Coverage + Evidence Strength + Verification Freshness + Verification Quality
Maximum = 100 points
```

| Dimension | Maximum |
| --- | ---: |
| Evidence Coverage | 30 |
| Evidence Strength | 30 |
| Verification Freshness | 20 |
| Verification Quality | 20 |

Decimal arithmetic is used internally. Only the final total is rounded half up to the nearest integer and clamped to `0-100`.

Policy version: `v1`.

## Evidence Coverage

All claims except `REJECTED` are applicable. A claim is supported only when its current status is `VERIFIED`, its latest verification is also `VERIFIED`, the verification is not expired at the reference time, and at least one evidence item referenced by that verification is attached to the claim and active.

```text
coverage = supported_claims / applicable_claims
coverage_points = coverage * 30
```

`PENDING`, `UNVERIFIED`, and `EXPIRED` claims contribute zero support. Expired claims remain in the denominator. Rejected claims are excluded. No claims produce zero coverage.

## Evidence Strength

Only supported claims are included. For each supported claim, active evidence IDs are deduplicated and the strongest evidence type is selected. Evidence strengths are not summed.

| Evidence type | Strength |
| --- | ---: |
| `TEST_REPORT` | 1.00 |
| `CERTIFICATION` | 0.95 |
| `MANUFACTURER_DOCUMENT` | 0.90 |
| `SUPPLIER_DOCUMENT` | 0.70 |
| `INTERNAL_REVIEW` | 0.60 |
| `SYSTEM_REVIEW` | 0.60 |
| `CUSTOMER_FEEDBACK` | 0.45 |
| `OTHER` or unknown | 0.30 |

```text
strength = average(strongest claim evidence)
strength_points = strength * 30
```

## Verification Freshness

The reference time is normalized to UTC. The freshness period is 365 days.

```text
age_days = max(0, reference_time - verified_at)
freshness = max(0, 1 - age_days / 365)
freshness_points = average(freshness) * 20
```

Verification at the reference time is `1.00`; at 365 days it is `0`. Expired verification has zero freshness and cannot support a claim.

## Verification Quality

Quality uses the method on the current verification and is averaged across supported claims.

| Verification method | Quality |
| --- | ---: |
| `TEST_REPORT` | 0.95 |
| `CERTIFICATION` | 0.95 |
| `MANUFACTURER_DOCUMENT` | 0.90 |
| `SUPPLIER_DOCUMENT` | 0.75 |
| `INTERNAL_REVIEW` | 0.70 |
| `SYSTEM_REVIEW` | 0.65 |
| `CUSTOMER_FEEDBACK` | 0.50 |
| `OTHER` or unknown | 0.40 |

```text
quality_points = average(current verification method quality) * 20
```

## Current State and History

Only the latest verification record controls a claim. Earlier verification records never stack. If the latest record is `REJECTED`, `PENDING`, or otherwise not a current valid `VERIFIED` record, the claim contributes zero.

## Data Sufficiency

- `NONE`: no supported verified claims.
- `LIMITED`: supported claims exist, but coverage is below 50% or fewer than 2 supported claims exist.
- `ADEQUATE`: at least 2 supported claims and coverage is at least 50%.
- `STRONG`: at least 3 supported claims and coverage is at least 75%.

A product with no meaningful Trust evidence receives score `0` and `Insufficient evidence`; this does not mean the product is bad.

## Customer Labels

- `90-100`: Very strong evidence
- `75-89`: Strong evidence
- `50-74`: Moderate evidence
- `25-49`: Limited evidence
- `0-24`: Insufficient evidence

## Reason Codes

The engine returns structured codes rather than customer-facing prose: `NO_TRUST_DATA`, `PARTIAL_EVIDENCE_COVERAGE`, `STRONG_EVIDENCE_COVERAGE`, `STRONG_SUPPORTING_EVIDENCE`, `LIMITED_SUPPORTING_EVIDENCE`, `RECENT_VERIFICATION`, `AGING_VERIFICATION`, `EXPIRED_VERIFICATION`, and `MULTIPLE_VERIFIED_CLAIMS`.
