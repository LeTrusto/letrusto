/**
 * Centralized registry for software/digital affiliate partnerships.
 *
 * RULE: Only add an entry here when LeTrusto has an approved, active affiliate
 * relationship with the provider. Do not pre-populate with unapproved programs.
 * Tool IDs must match the slug used in the AI tools catalog.
 */

export type AffiliateStatus = "active" | "pending" | "inactive" | "none";

export type SoftwareAffiliate = {
  /** Matches the slug in the AI tools catalog */
  toolSlug: string;
  providerName: string;
  status: AffiliateStatus;
  /** Tracking URL supplied by the affiliate program */
  affiliateUrl: string | null;
  /** Provider's public website (non-affiliate) */
  officialUrl: string;
  /** Affiliate network or platform managing the relationship */
  network: string | null;
  /** ISO date the relationship was last verified */
  verifiedDate: string;
  /** Displayed in disclosures near affiliate CTAs */
  disclosureNote: string;
};

/**
 * Registry of software affiliate programs.
 * Status must be "active" for a URL to be surfaced to users.
 */
export const SOFTWARE_AFFILIATES: SoftwareAffiliate[] = [
  {
    toolSlug: "elevenlabs",
    providerName: "ElevenLabs",
    status: "active",
    affiliateUrl: "https://try.elevenlabs.io/l893urztlad5",
    officialUrl: "https://elevenlabs.io",
    network: "PartnerStack",
    verifiedDate: "2026-08-10",
    disclosureNote:
      "LeTrusto is an approved affiliate partner of ElevenLabs. We may earn a commission when you sign up through our link.",
  },
  {
    toolSlug: "highlevel",
    providerName: "HighLevel",
    status: "active",
    // TODO: Replace with real HighLevel affiliate tracking URL from dashboard.
    affiliateUrl: null,
    officialUrl: "https://www.gohighlevel.com",
    network: null,
    verifiedDate: "2026-08-11",
    disclosureNote:
      "LeTrusto is an approved affiliate partner of HighLevel. We may earn a commission when you sign up through our link.",
  },
  {
    toolSlug: "moosend",
    providerName: "Moosend",
    status: "active",
    // TODO: Replace with real Moosend affiliate tracking URL from dashboard.
    affiliateUrl: null,
    officialUrl: "https://moosend.com",
    network: null,
    verifiedDate: "2026-08-11",
    disclosureNote:
      "LeTrusto is an approved affiliate partner of Moosend. We may earn a commission when you sign up through our link.",
  },
  {
    toolSlug: "beehiiv",
    providerName: "beehiiv",
    status: "active",
    // TODO: Replace with real beehiiv affiliate tracking URL from dashboard.
    affiliateUrl: null,
    officialUrl: "https://www.beehiiv.com",
    network: null,
    verifiedDate: "2026-08-11",
    disclosureNote:
      "LeTrusto is an approved affiliate partner of beehiiv. We may earn a commission when you sign up through our link.",
  },
];

/** Returns the affiliate entry for a tool slug if the relationship is active. */
export function getActiveSoftwareAffiliate(
  toolSlug: string
): SoftwareAffiliate | null {
  return (
    SOFTWARE_AFFILIATES.find(
      (a) => a.toolSlug === toolSlug && a.status === "active"
    ) ?? null
  );
}

/** Returns true only when the tool has a confirmed active affiliate relationship. */
export function hasSoftwareAffiliate(toolSlug: string): boolean {
  return getActiveSoftwareAffiliate(toolSlug) !== null;
}
