/**
 * Centralized registry for software/digital affiliate partnerships.
 * Legacy — cleared during POD pivot. Kept for type compatibility.
 */

export type AffiliateStatus = "active" | "pending" | "inactive" | "none";

export type SoftwareAffiliate = {
  toolSlug: string;
  providerName: string;
  status: AffiliateStatus;
  affiliateUrl: string | null;
  officialUrl: string;
  network: string | null;
  verifiedDate: string;
  disclosureNote: string;
};

export const SOFTWARE_AFFILIATES: SoftwareAffiliate[] = [];

export function getActiveSoftwareAffiliate(
  toolSlug: string
): SoftwareAffiliate | null {
  return (
    SOFTWARE_AFFILIATES.find(
      (a) => a.toolSlug === toolSlug && a.status === "active"
    ) ?? null
  );
}

export function hasSoftwareAffiliate(toolSlug: string): boolean {
  return getActiveSoftwareAffiliate(toolSlug) !== null;
}
