"use client";

import { ExternalLink } from "lucide-react";
import Link from "next/link";

import { getActiveSoftwareAffiliate, type SoftwareAffiliate } from "@/lib/softwareAffiliates";

type AffiliateCTAProps = {
  toolSlug: string;
  toolName: string;
  websiteUrl: string;
  /** Backend affiliate fields — used as fallback if frontend registry has no entry */
  backendAffiliateAvailable?: boolean;
  backendAffiliateUrl?: string | null;
  ctaLabel?: string;
  className?: string;
};

function resolveAffiliate(
  props: AffiliateCTAProps
): { url: string; disclosure: string } | null {
  const entry: SoftwareAffiliate | null = getActiveSoftwareAffiliate(props.toolSlug);

  if (entry?.affiliateUrl) {
    return { url: entry.affiliateUrl, disclosure: entry.disclosureNote };
  }

  if (props.backendAffiliateAvailable && props.backendAffiliateUrl) {
    return {
      url: props.backendAffiliateUrl,
      disclosure: `LeTrusto may earn a commission when you sign up through this link.`,
    };
  }

  return null;
}

export default function AffiliateCTA({
  toolSlug,
  toolName,
  websiteUrl,
  backendAffiliateAvailable,
  backendAffiliateUrl,
  ctaLabel,
  className = "",
}: AffiliateCTAProps) {
  const affiliate = resolveAffiliate({
    toolSlug,
    toolName,
    websiteUrl,
    backendAffiliateAvailable,
    backendAffiliateUrl,
  });

  const hasAffiliate = affiliate !== null;

  return (
    <div className={`lt-card rounded-[var(--radius-xl)] ${className}`}>
      <div className="flex flex-wrap items-center gap-3">
        {hasAffiliate ? (
          <a
            href={affiliate.url}
            target="_blank"
            rel="noreferrer sponsored"
            className="lt-btn lt-btn-lg lt-btn-brand"
          >
            {ctaLabel || `Try ${toolName}`}
            <ExternalLink className="h-4 w-4" />
          </a>
        ) : (
          <a
            href={websiteUrl}
            target="_blank"
            rel="noreferrer"
            className="lt-btn lt-btn-lg lt-btn-primary"
          >
            Visit {toolName}
            <ExternalLink className="h-4 w-4" />
          </a>
        )}

        {hasAffiliate && (
          <a
            href={websiteUrl}
            target="_blank"
            rel="noreferrer"
            className="lt-btn lt-btn-lg lt-btn-secondary"
          >
            Official website (non-affiliate)
          </a>
        )}

        <Link href="/ai-tools" className="lt-btn lt-btn-lg lt-btn-ghost">
          ← Back to AI Tools
        </Link>
      </div>

      {hasAffiliate && (
        <p className="mt-4 text-xs leading-relaxed text-[var(--text-muted)]">
          {affiliate.disclosure}{" "}
          This does not change the price you pay.{" "}
          <Link href="/affiliate-disclosure" className="underline transition hover:text-[var(--lt-purple)]">
            Full disclosure
          </Link>
        </p>
      )}
    </div>
  );
}
