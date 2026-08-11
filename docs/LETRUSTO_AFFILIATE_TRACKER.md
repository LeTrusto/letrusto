# LeTrusto Affiliate Tracker

> Last updated: 2026-08-11
> Source: User-provided application status + repository verification

---

## Active / Approved Programs

| Program | Platform/Network | Status | Commission | Cookie/Duration | Affiliate Link Available | Application Date | Notes |
|---------|-----------------|--------|------------|-----------------|--------------------------|-----------------|-------|
| ElevenLabs | PartnerStack | **Active** | Verify in dashboard | Verify in dashboard | Yes — `try.elevenlabs.io/l893urztlad5` | Pre-2026-08-10 | Configured in backend migration `20260810_01` and `lib/softwareAffiliates.ts`. Used in pricing guide and comparison guide. |
| HighLevel | Unknown | **Active** | 40% recurring | Unknown | Verify in dashboard | Unknown | User-confirmed approved/active. Commission rate user-provided. |
| Moosend | Unknown | **Active** | Unknown | Unknown | User says received | Unknown | User-confirmed approved/onboarded. Affiliate link received but not yet configured in codebase. |
| beehiiv | Unknown | **Active** | 50% for 12 months | Unknown | Verify in dashboard | Unknown | User-confirmed approved/active. Commission rate user-provided. |

## Pending Applications

| Program | Platform/Network | Status | Commission | Cookie/Duration | Affiliate Link Available | Application Date | Notes |
|---------|-----------------|--------|------------|-----------------|--------------------------|-----------------|-------|
| Semrush | Unknown | **Pending** | Unknown | Unknown | No | Unknown | Application submitted, awaiting decision. |
| Murf AI | Unknown | **Pending** | Unknown | Unknown | No | Unknown | Application submitted, awaiting decision. Featured in comparison guide. |
| Surfer | Unknown | **Pending** | Unknown | Unknown | No | Unknown | Application submitted, awaiting decision. |
| Grammarly | Unknown | **Pending** | Unknown | Unknown | No | Unknown | Application submitted, awaiting decision. |
| Miro | Unknown | **Pending** | Unknown | Unknown | No | Unknown | Application submitted, awaiting decision. |
| Synthesia | Unknown | **Pending** | Unknown | Unknown | No | Unknown | Application submitted, awaiting decision. |

## Rejected / Limited

| Program | Platform/Network | Status | Notes |
|---------|-----------------|--------|-------|
| PartnerStack (network-level) | PartnerStack | **Limited/Rejected** | Network profile access was limited/rejected. Existing individual PartnerStack partnerships (e.g., ElevenLabs) are not necessarily affected. |

## Amazon Associates (Legacy Product System)

| Program | Status | Tag | Notes |
|---------|--------|-----|-------|
| Amazon India Associates | Unknown | `letrusto-21` | Configured in `lib/affiliate.ts` via env variable `NEXT_PUBLIC_AMAZON_ASSOCIATE_ID`. Part of legacy product marketplace system. Approval status not verified. |

## Flipkart Affiliate (Legacy Product System)

| Program | Status | Notes |
|---------|--------|-------|
| Flipkart Affiliate | Unknown | URL passthrough in `lib/affiliate.ts`. Part of legacy product marketplace system. No tracking tag configured. Approval status not verified. |

---

## Integration Status in Codebase

| Program | In `softwareAffiliates.ts` | In Backend DB | In Guide Pages | In Homepage |
|---------|---------------------------|---------------|----------------|-------------|
| ElevenLabs | Yes (active) | Yes (migration 20260810_01) | Yes (pricing + comparison) | No |
| HighLevel | No | No | No | No |
| Moosend | No | No | No | No |
| beehiiv | No | No | No | No |
| Others | No | No | No | No |

---

## Rules

1. Only add an entry to `lib/softwareAffiliates.ts` when LeTrusto has an **approved, active** affiliate relationship with verified tracking URL.
2. Do not fabricate commission rates, cookie durations, or approval statuses.
3. Mark unknown values as "Unknown" or "Verify in dashboard".
4. Distinguish clearly between Approved, Pending, Rejected, Active, and Unknown statuses.
5. Update this tracker whenever an affiliate application status changes.
