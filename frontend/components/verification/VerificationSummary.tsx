import { Check, Clock3, ShieldCheck } from "lucide-react";

import { verificationCheckLabels, verificationDate, type PublicVerification } from "@/utils/verification";

export function VerificationSummary({ verification, compact = false }: { verification: PublicVerification; compact?: boolean }) {
  const completed = verificationCheckLabels.filter(([key]) => verification.checks[key]);
  const reviewed = verificationDate(verification.reviewed_at);
  return (
    <section className={`verification-summary ${compact ? "verification-summary-compact" : ""}`} aria-labelledby="verification-title">
      <div className="verification-summary-heading">
        <div className="verification-summary-icon"><ShieldCheck size={18} /></div>
        <div><p className="eyebrow">Trust &amp; verification</p><h2 id="verification-title">{verification.label}</h2></div>
      </div>
      {completed.length ? <ul className="verification-checklist">{completed.map(([key, label]) => <li key={key}><Check size={15} aria-hidden="true" /><span>{label}</span></li>)}</ul> : <p className="verification-muted"><Clock3 size={15} /> No verification checks are currently marked complete.</p>}
      {reviewed && <p className="verification-reviewed">Last reviewed: {reviewed}</p>}
      {!compact && <details className="verification-explanation"><summary>How verification works</summary><ol><li>The seller submits property information.</li><li>Our team reviews the submitted information.</li><li>Where applicable, we verify contact and review the seller/property relationship.</li><li>Supporting document evidence may be reviewed.</li><li>Available verification information is shown transparently on the property page.</li></ol><p>Verification does not replace independent legal, title, financial, or property due diligence before purchase.</p></details>}
    </section>
  );
}
