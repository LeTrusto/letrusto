"use client";

import { AlertCircle, CheckCircle2, Clock3, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { getPublicProductTrust, type PublicTrustClaim, type PublicTrustResponse, type PublicTrustStatus } from "@/services/trust.service";

function claimLabel(value: string) {
  return value.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" }) : null;
}

function statusCopy(status: PublicTrustStatus) {
  switch (status) {
    case "VERIFIED":
      return { label: "Verified by LeTrusto", className: "border-green-200 bg-green-50 text-green-900" };
    case "PENDING":
      return { label: "Verification in progress", className: "border-amber-200 bg-amber-50 text-amber-950" };
    case "EXPIRED":
      return { label: "Verification needs to be renewed", className: "border-slate-200 bg-slate-50 text-slate-700" };
    default:
      return { label: "Supplier claim - not independently verified", className: "border-[var(--border)] bg-[var(--surface-muted)] text-[var(--text-secondary)]" };
  }
}

function StatusIcon({ status }: { status: PublicTrustStatus }) {
  if (status === "VERIFIED") return <CheckCircle2 size={18} className="text-green-700" aria-hidden="true" />;
  if (status === "PENDING") return <Clock3 size={18} className="text-amber-700" aria-hidden="true" />;
  if (status === "EXPIRED") return <AlertCircle size={18} className="text-slate-500" aria-hidden="true" />;
  return <ShieldCheck size={18} className="text-[var(--text-muted)]" aria-hidden="true" />;
}

function TrustClaim({ claim }: { claim: PublicTrustClaim }) {
  const copy = statusCopy(claim.status);
  const verifiedDate = formatDate(claim.verified_at);
  const canExplain = claim.status === "VERIFIED" || claim.status === "EXPIRED" || Boolean(claim.verification_method);

  return (
    <div className={`rounded-lg border p-4 ${copy.className}`}>
      <div className="flex items-start gap-3">
        <StatusIcon status={claim.status} />
        <div className="min-w-0 flex-1">
          <p className="font-semibold">{claimLabel(claim.claim_type)}{claim.status === "VERIFIED" ? " verified" : ""}</p>
          <p className="mt-1 text-sm font-medium">{claim.claim_value}</p>
          <p className="mt-2 text-xs">{copy.label}</p>
          {canExplain && (
            <details className="mt-3 border-t border-current/15 pt-3">
              <summary className="cursor-pointer text-xs font-semibold">{claim.status === "VERIFIED" ? "Why is this verified?" : "View verification details"}</summary>
              <div className="mt-3 space-y-2 text-xs">
                {claim.verification_method && <p><span className="font-semibold">Verification:</span> {claim.verification_method}.</p>}
                {verifiedDate && <p><span className="font-semibold">Reviewed:</span> {verifiedDate}</p>}
                {claim.evidence_summary.length > 0 && (
                  <div>
                    <p className="font-semibold">Evidence reviewed:</p>
                    <ul className="mt-1 list-disc space-y-1 pl-4">
                      {claim.evidence_summary.map((evidence) => <li key={`${evidence.evidence_type}-${evidence.title}`}>{evidence.title} ({claimLabel(evidence.evidence_type)}){evidence.description ? ` - ${evidence.description}` : ""}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            </details>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ProductTrustSection({ productId }: { productId: string }) {
  const [trust, setTrust] = useState<PublicTrustResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getPublicProductTrust(productId)
      .then((response) => { if (!cancelled) setTrust(response); })
      .catch(() => { if (!cancelled) setFailed(true); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [productId]);

  if (loading) return <section aria-label="Trust information" className="mt-5 border-t border-[var(--border)] pt-5"><div className="h-4 w-48 animate-pulse rounded bg-[var(--surface-muted)]" /><div className="mt-3 h-16 animate-pulse rounded-lg bg-[var(--surface-muted)]" /></section>;
  if (failed) return <p className="mt-5 border-t border-[var(--border)] pt-5 text-xs text-[var(--text-muted)]">Trust information is currently unavailable.</p>;
  if (!trust || trust.claims.length === 0) return null;

  return (
    <section aria-labelledby="product-trust-heading" className="mt-6 border-t border-[var(--border)] pt-5">
      <div className="flex items-start gap-3">
        <ShieldCheck size={20} className="mt-0.5 text-[var(--lt-primary)]" aria-hidden="true" />
        <div>
          <h2 id="product-trust-heading" className="text-base font-bold text-[var(--text-primary)]">Why you can trust this product</h2>
          <p className="mt-1 text-xs text-[var(--text-muted)]">See exactly what LeTrusto has verified and what remains a supplier claim.</p>
        </div>
      </div>
      <div className="mt-4 space-y-3">
        {trust.claims.map((claim) => <TrustClaim key={`${claim.claim_type}-${claim.claim_value}`} claim={claim} />)}
      </div>
    </section>
  );
}
