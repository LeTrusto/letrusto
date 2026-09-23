import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { VerificationSummary } from "@/components/verification/VerificationSummary";
import type { PublicVerification } from "@/utils/verification";

const verification = (status: PublicVerification["status"], label: string, checks: PublicVerification["checks"], reviewed_at: string | null = null): PublicVerification => ({ status, label, checks, reviewed_at });

describe("VerificationSummary", () => {
  it("renders completed checks and the due-diligence explanation", () => {
    const html = renderToStaticMarkup(<VerificationSummary verification={verification("DOCUMENT_EVIDENCE_REVIEWED", "Document evidence reviewed", { contact_verified: false, relationship_reviewed: false, document_evidence_reviewed: true }, "2026-09-23T00:00:00Z")} />);
    expect(html).toContain("Trust &amp; verification");
    expect(html).toContain("Document evidence reviewed");
    expect(html).toContain("Last reviewed");
    expect(html).toContain("How verification works");
    expect(html).toContain("does not replace independent legal");
    expect(html).not.toContain("Contact verified</span>");
  });

  it("does not present an unreviewed property as verified", () => {
    const html = renderToStaticMarkup(<VerificationSummary verification={verification("NOT_REVIEWED", "Verification not yet reviewed", { contact_verified: false, relationship_reviewed: false, document_evidence_reviewed: false })} />);
    expect(html).toContain("No verification checks are currently marked complete.");
    expect(html).not.toContain("verification-checklist");
  });

  it("handles expired verification conservatively", () => {
    const html = renderToStaticMarkup(<VerificationSummary compact verification={verification("EXPIRED", "Verification requires re-review", { contact_verified: false, relationship_reviewed: false, document_evidence_reviewed: false })} />);
    expect(html).toContain("Verification requires re-review");
    expect(html).not.toContain("How verification works");
  });
});
