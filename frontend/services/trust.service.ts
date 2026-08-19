import { apiRequest } from "@/services/api";

export type PublicTrustStatus = "VERIFIED" | "PENDING" | "UNVERIFIED" | "EXPIRED";

export type PublicTrustEvidenceSummary = {
  evidence_type: string;
  title: string;
  description: string | null;
};

export type PublicTrustClaim = {
  claim_type: string;
  claim_value: string;
  status: PublicTrustStatus;
  verified_at: string | null;
  verification_method: string | null;
  evidence_summary: PublicTrustEvidenceSummary[];
};

export type PublicTrustResponse = {
  product_id: string;
  claims: PublicTrustClaim[];
};

export function getPublicProductTrust(productId: string) {
  return apiRequest<PublicTrustResponse>(`/products/${encodeURIComponent(productId)}/trust`);
}
