export type VerificationStatus =
  | "NOT_REVIEWED"
  | "CONTACT_VERIFIED"
  | "RELATIONSHIP_REVIEWED"
  | "DOCUMENT_EVIDENCE_REVIEWED"
  | "FAILED"
  | "EXPIRED"
  | string;

export type PublicVerification = {
  status: VerificationStatus;
  label: string;
  checks: {
    contact_verified: boolean;
    relationship_reviewed: boolean;
    document_evidence_reviewed: boolean;
  };
  reviewed_at: string | null;
};

export const verificationCheckLabels = [
  ["contact_verified", "Contact verified"],
  ["relationship_reviewed", "Seller/property relationship reviewed"],
  ["document_evidence_reviewed", "Document evidence reviewed"],
] as const;

const verificationLabels: Record<string, string> = {
  NOT_REVIEWED: "Verification not yet reviewed",
  CONTACT_VERIFIED: "Contact verified",
  RELATIONSHIP_REVIEWED: "Seller/property relationship reviewed",
  DOCUMENT_EVIDENCE_REVIEWED: "Document evidence reviewed",
  FAILED: "Verification unavailable",
  EXPIRED: "Verification requires re-review",
};

export function verificationLabelForStatus(status: string): string {
  return verificationLabels[status] || "Verification not yet reviewed";
}

export function verificationChecksForStatus(status: string): Record<string, boolean> {
  return {
    contact_verified: status === "CONTACT_VERIFIED",
    relationship_reviewed: status === "RELATIONSHIP_REVIEWED",
    document_evidence_reviewed: status === "DOCUMENT_EVIDENCE_REVIEWED",
  };
}

export function verificationFromStatus(status: string, reviewedAt: string | null = null): PublicVerification {
  return {
    status,
    label: verificationLabelForStatus(status),
    checks: verificationChecksForStatus(status) as PublicVerification["checks"],
    reviewed_at: reviewedAt,
  };
}

export function verificationBadgeLabel(verification: PublicVerification | null | undefined): string | null {
  if (!verification || !["CONTACT_VERIFIED", "RELATIONSHIP_REVIEWED", "DOCUMENT_EVIDENCE_REVIEWED"].includes(verification.status)) return null;
  return verification.label;
}

export function verificationDate(value: string | null): string | null {
  if (!value) return null;
  return new Date(value).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}
