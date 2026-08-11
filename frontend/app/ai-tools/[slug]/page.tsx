import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import Script from "next/script";
import { CheckCircle2, XCircle, Sparkles, ExternalLink } from "lucide-react";

import AffiliateCTA from "@/components/AffiliateCTA";
import { getAiToolBySlug } from "@/services/ai-tools.service";
import { getActiveSoftwareAffiliate } from "@/lib/softwareAffiliates";

type Props = {
  params: Promise<{ slug: string }>;
};

function formatPricing(toolPricing: {
  model: string | null;
  amount: number | null;
  currency: string | null;
  period: string | null;
  notes: string | null;
}) {
  if (!toolPricing.model) return "Not publicly verified";
  if (toolPricing.amount !== null && toolPricing.currency && toolPricing.period) {
    return `${toolPricing.currency} ${toolPricing.amount} / ${toolPricing.period}`;
  }
  return toolPricing.notes || toolPricing.model.replace("_", " ");
}

function pricingBadges(pricing: {
  hasFreePlan: boolean | null;
  hasFreeTrial: boolean | null;
  trialDays: number | null;
}) {
  const badges: string[] = [];
  if (pricing.hasFreePlan) badges.push("Free plan available");
  if (pricing.hasFreeTrial) {
    badges.push(pricing.trialDays ? `${pricing.trialDays}-day free trial` : "Free trial available");
  }
  return badges;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const tool = await getAiToolBySlug(slug);

  if (!tool) {
    return { title: "AI Tool Not Found", description: "The requested AI tool page could not be found." };
  }

  const title = `${tool.name} — ${tool.category.name} | Review`;
  const description = tool.description.length > 155
    ? tool.description.slice(0, 152) + "..."
    : tool.description;

  return {
    title,
    description,
    alternates: { canonical: `/ai-tools/${tool.slug}` },
    openGraph: {
      title,
      description,
      url: `/ai-tools/${tool.slug}`,
      siteName: "LeTrusto",
      type: "article",
      images: [{ url: tool.logoUrl || "/images/og-default.svg", width: 1200, height: 630 }],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [tool.logoUrl || "/images/og-default.svg"],
    },
  };
}

export default async function AIToolDetailPage({ params }: Props) {
  const { slug } = await params;
  const tool = await getAiToolBySlug(slug);

  if (!tool) {
    return (
      <main className="min-h-screen bg-[var(--surface-soft)] px-6 py-16">
        <div className="lt-card mx-auto max-w-4xl rounded-[var(--radius-2xl)] p-10 text-center">
          <h1 className="lt-heading-1">AI Tool Not Found</h1>
          <p className="lt-body mt-3">This tool is unavailable or not currently published.</p>
          <Link href="/ai-tools" className="lt-btn lt-btn-md lt-btn-primary mt-6">Back to AI Tools</Link>
        </div>
      </main>
    );
  }

  const pricingText = formatPricing(tool.pricing);
  const lastVerified = tool.lastVerifiedAt
    ? new Date(tool.lastVerifiedAt).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })
    : null;
  const pBadges = pricingBadges(tool.pricing);
  const affiliate = getActiveSoftwareAffiliate(tool.slug);
  const hasAffiliate = Boolean(affiliate?.affiliateUrl) || Boolean(tool.affiliateAvailable && tool.affiliateUrl);

  const schema = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: tool.name,
    applicationCategory: tool.category.name,
    operatingSystem: tool.platforms.join(", ") || undefined,
    description: tool.description,
    publisher: { "@type": "Organization", name: tool.provider },
    offers: tool.pricing.pricingUrl
      ? { "@type": "Offer", url: tool.pricing.pricingUrl, priceCurrency: tool.pricing.currency || undefined, price: tool.pricing.amount ?? undefined }
      : undefined,
    url: tool.websiteUrl,
  };

  return (
    <main className="min-h-screen bg-[var(--surface-soft)] px-6 pb-16 pt-10">
      <Script id="ai-tool-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />

      <div className="mx-auto max-w-5xl space-y-10">
        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="text-xs text-[var(--text-muted)]">
          <ol className="flex flex-wrap items-center gap-1">
            <li><Link href="/" className="lt-link">Home</Link></li>
            <li aria-hidden="true" className="text-[var(--border)]">/</li>
            <li><Link href="/ai-tools" className="lt-link">AI Tools</Link></li>
            <li aria-hidden="true" className="text-[var(--border)]">/</li>
            <li><Link href={`/category/${tool.category.slug}`} className="lt-link">{tool.category.name}</Link></li>
            <li aria-hidden="true" className="text-[var(--border)]">/</li>
            <li className="font-medium text-[var(--text-primary)]" aria-current="page">{tool.name}</li>
          </ol>
        </nav>

        {/* ── Hero ──────────────────────────────────────────── */}
        <header className="lt-card rounded-[var(--radius-2xl)] p-8 md:p-10">
          <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
            <div className="min-w-0 max-w-3xl">
              <span className="lt-badge lt-badge-brand">{tool.category.name}</span>
              <h1 className="lt-heading-1 mt-3">{tool.name}</h1>
              <p className="mt-1 text-[var(--text-secondary)]">by {tool.provider}</p>
              <p className="lt-body mt-4">{tool.description}</p>

              <div className="mt-6 flex flex-wrap items-center gap-3">
                {hasAffiliate ? (
                  <a
                    href={affiliate?.affiliateUrl || tool.affiliateUrl || "#"}
                    target="_blank"
                    rel="noreferrer sponsored"
                    className="lt-btn lt-btn-lg lt-btn-brand"
                  >
                    Try {tool.name} <ExternalLink className="h-4 w-4" />
                  </a>
                ) : (
                  <a href={tool.websiteUrl} target="_blank" rel="noreferrer" className="lt-btn lt-btn-lg lt-btn-primary">
                    Visit {tool.name} <ExternalLink className="h-4 w-4" />
                  </a>
                )}
                <Link href="/compare" className="lt-btn lt-btn-lg lt-btn-secondary">Compare options</Link>
              </div>

              {hasAffiliate && (
                <p className="mt-3 text-xs text-[var(--text-muted)]">
                  Affiliate link — LeTrusto may earn a commission at no extra cost to you.{" "}
                  <Link href="/affiliate-disclosure" className="underline hover:text-[var(--lt-purple)]">Disclosure</Link>
                </p>
              )}
            </div>
            {tool.logoUrl ? (
              <Image src={tool.logoUrl} alt={`${tool.name} logo`} width={80} height={80}
                className="h-20 w-20 shrink-0 rounded-[var(--radius-xl)] border border-[var(--border)] bg-white object-contain p-3"
                unoptimized />
            ) : null}
          </div>

          {tool.tags.length > 0 && (
            <div className="mt-6 flex flex-wrap gap-2">
              {tool.tags.map((tag) => <span key={tag} className="lt-badge">{tag}</span>)}
            </div>
          )}
        </header>

        {/* ── Who is it for? ────────────────────────────────── */}
        {tool.bestFor.length > 0 && (
          <section className="lt-card rounded-[var(--radius-2xl)] p-8">
            <h2 className="lt-heading-2">Who is {tool.name} for?</h2>
            <ul className="mt-4 grid gap-3 sm:grid-cols-2">
              {tool.bestFor.map((item) => (
                <li key={item} className="flex items-start gap-3 text-[var(--text-secondary)]">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-500" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
            {tool.notIdealFor.length > 0 && (
              <>
                <h3 className="lt-heading-3 mt-8">May not be the right fit for</h3>
                <ul className="mt-3 grid gap-3 sm:grid-cols-2">
                  {tool.notIdealFor.map((item) => (
                    <li key={item} className="flex items-start gap-3 text-[var(--text-secondary)]">
                      <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-rose-400" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </section>
        )}

        {/* ── Key Capabilities ──────────────────────────────── */}
        {tool.features.length > 0 && (
          <section className="lt-card rounded-[var(--radius-2xl)] p-8">
            <h2 className="lt-heading-2">Key Capabilities</h2>
            <ul className="mt-4 grid gap-2 sm:grid-cols-2">
              {tool.features.map((item) => (
                <li key={item} className="flex items-start gap-2.5 text-[var(--text-secondary)]">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--lt-purple)]" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* ── Use Cases ─────────────────────────────────────── */}
        {tool.useCases.length > 0 && (
          <section className="lt-card rounded-[var(--radius-2xl)] p-8">
            <h2 className="lt-heading-2">Common Use Cases</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {tool.useCases.map((item) => (
                <div key={item} className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface-soft)] px-4 py-3 text-sm font-medium text-[var(--text-primary)]">
                  {item}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── Strengths & Limitations ───────────────────────── */}
        <div className="grid gap-6 lg:grid-cols-2">
          {tool.pros.length > 0 && (
            <section className="lt-card rounded-[var(--radius-2xl)] border-emerald-200 bg-emerald-50/30 p-8">
              <h2 className="lt-heading-3 text-emerald-800">Strengths</h2>
              <ul className="mt-4 space-y-3">
                {tool.pros.map((item) => (
                  <li key={item} className="flex items-start gap-2.5 text-emerald-900">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                    <span className="text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {tool.cons.length > 0 && (
            <section className="lt-card rounded-[var(--radius-2xl)] border-rose-200 bg-rose-50/30 p-8">
              <h2 className="lt-heading-3 text-rose-800">Limitations</h2>
              <ul className="mt-4 space-y-3">
                {tool.cons.map((item) => (
                  <li key={item} className="flex items-start gap-2.5 text-rose-900">
                    <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-400" />
                    <span className="text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        {/* ── Pricing ───────────────────────────────────────── */}
        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">Pricing</h2>
          <p className="lt-body mt-3">{pricingText}</p>
          {pBadges.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {pBadges.map((b) => <span key={b} className="lt-badge lt-badge-brand">{b}</span>)}
            </div>
          )}
          {tool.pricing.pricingUrl && (
            <a href={tool.pricing.pricingUrl} target="_blank" rel="noreferrer" className="lt-btn lt-btn-md lt-btn-secondary mt-5">
              View official pricing <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
          <p className="mt-5 text-xs text-[var(--text-muted)]">
            Software pricing changes frequently. Always verify current rates with the provider.
            {lastVerified && <> Last checked: {lastVerified}.</>}
          </p>
        </section>

        {/* ── Platforms & Integrations ───────────────────────── */}
        {(tool.platforms.length > 0 || tool.integrations.length > 0) && (
          <section className="lt-card rounded-[var(--radius-2xl)] p-8">
            <h2 className="lt-heading-2">Platforms &amp; Integrations</h2>
            <div className="mt-4 grid gap-6 sm:grid-cols-2">
              {tool.platforms.length > 0 && (
                <div>
                  <h3 className="lt-label mb-3">Platforms</h3>
                  <div className="flex flex-wrap gap-2">
                    {tool.platforms.map((p) => <span key={p} className="lt-badge">{p}</span>)}
                  </div>
                </div>
              )}
              {tool.integrations.length > 0 && (
                <div>
                  <h3 className="lt-label mb-3">Integrations</h3>
                  <div className="flex flex-wrap gap-2">
                    {tool.integrations.map((i) => <span key={i} className="lt-badge">{i}</span>)}
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {/* ── LeTrusto Recommendation ───────────────────────── */}
        {tool.whyLetrustoRecommends && (
          <section className="lt-card rounded-[var(--radius-2xl)] border-[var(--lt-purple-light)] bg-[rgba(124,58,237,0.03)] p-8">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-[var(--lt-purple)]" />
              <h2 className="lt-heading-3 text-[var(--lt-purple-dark)]">LeTrusto Recommendation</h2>
            </div>
            <p className="lt-body mt-3">{tool.whyLetrustoRecommends}</p>
            {lastVerified && <p className="mt-4 text-xs text-[var(--text-muted)]">Last verified: {lastVerified}</p>}
          </section>
        )}

        {/* ── Explore More ──────────────────────────────────── */}
        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-3">Explore More</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <Link href={`/category/${tool.category.slug}`} className="lt-btn lt-btn-md lt-btn-secondary w-full justify-center">
              More {tool.category.name}
            </Link>
            <Link href="/compare" className="lt-btn lt-btn-md lt-btn-secondary w-full justify-center">
              Compare Tools
            </Link>
            <Link href="/ai" className="lt-btn lt-btn-md lt-btn-secondary w-full justify-center">
              <Sparkles className="h-4 w-4" /> Ask LeTrusto
            </Link>
          </div>
        </section>

        {/* ── Final CTA ─────────────────────────────────────── */}
        <AffiliateCTA
          toolSlug={tool.slug}
          toolName={tool.name}
          websiteUrl={tool.websiteUrl}
          backendAffiliateAvailable={tool.affiliateAvailable}
          backendAffiliateUrl={tool.affiliateUrl}
        />
      </div>
    </main>
  );
}
