import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import Script from "next/script";

import AffiliateCTA from "@/components/AffiliateCTA";
import { getAiToolBySlug } from "@/services/ai-tools.service";

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
  if (!toolPricing.model) {
    return "Not publicly verified";
  }

  if (toolPricing.amount !== null && toolPricing.currency && toolPricing.period) {
    return `${toolPricing.currency} ${toolPricing.amount} / ${toolPricing.period}`;
  }

  return toolPricing.notes || toolPricing.model.replace("_", " ");
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const tool = await getAiToolBySlug(slug);

  if (!tool) {
    return {
      title: "AI Tool Not Found",
      description: "The requested AI tool page could not be found.",
    };
  }

  const title = `${tool.name} Review`;
  const description = `${tool.name} by ${tool.provider}. Category: ${tool.category.name}. ${tool.description}`;

  return {
    title,
    description,
    alternates: {
      canonical: `/ai-tools/${tool.slug}`,
    },
    openGraph: {
      title,
      description,
      url: `/ai-tools/${tool.slug}`,
      siteName: "LeTrusto",
      type: "website",
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
          <Link href="/ai-tools" className="lt-btn lt-btn-md lt-btn-primary mt-6">
            Back to AI Tools
          </Link>
        </div>
      </main>
    );
  }

  const pricingText = formatPricing(tool.pricing);
  const lastVerifiedDate = tool.lastVerifiedAt
    ? new Date(tool.lastVerifiedAt).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })
    : "Not available";

  const schema = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: tool.name,
    applicationCategory: tool.category.name,
    operatingSystem: tool.platforms.join(", ") || undefined,
    description: tool.description,
    publisher: {
      "@type": "Organization",
      name: tool.provider,
    },
    offers: tool.pricing.pricingUrl
      ? {
          "@type": "Offer",
          url: tool.pricing.pricingUrl,
          priceCurrency: tool.pricing.currency || undefined,
          price: tool.pricing.amount ?? undefined,
        }
      : undefined,
    url: tool.websiteUrl,
  };

  return (
    <main className="min-h-screen bg-[var(--surface-soft)] px-6 py-12">
      <Script id="ai-tool-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />

      <div className="mx-auto max-w-6xl space-y-8">
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

        <div className="lt-card rounded-[var(--radius-2xl)] p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div className="min-w-0">
              <p className="lt-label text-[var(--lt-purple)]">{tool.category.name}</p>
              <h1 className="lt-heading-1 mt-2">{tool.name}</h1>
              <p className="mt-2 text-lg text-[var(--text-secondary)]">Provider: {tool.provider}</p>
              <p className="lt-body mt-4 max-w-3xl">{tool.description}</p>
            </div>
            {tool.logoUrl ? (
              <Image
                src={tool.logoUrl}
                alt={`${tool.name} logo`}
                width={64}
                height={64}
                className="h-16 w-16 rounded-xl border border-slate-200 bg-white object-contain p-2"
                unoptimized
              />
            ) : null}
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {tool.tags.map((tag) => (
              <span key={tag} className="lt-badge">
                {tag}
              </span>
            ))}
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-900">Pricing</h2>
            <p className="mt-3 text-slate-700">{pricingText}</p>
            {tool.pricing.pricingUrl ? (
              <a
                href={tool.pricing.pricingUrl}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:border-slate-500"
              >
                View official pricing
              </a>
            ) : null}
            <p className="mt-4 text-xs text-slate-400">
              Pricing verified against official sources. Software pricing changes — always confirm current rates with the provider.
            </p>
          </section>

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-900">Why LeTrusto Recommends</h2>
            <p className="mt-3 text-slate-700">{tool.whyLetrustoRecommends || "Not yet documented."}</p>
            <p className="mt-4 text-sm text-slate-500">Last verified: {lastVerifiedDate}</p>
          </section>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-3xl border border-emerald-200 bg-emerald-50/40 p-6">
            <h2 className="text-xl font-bold text-emerald-800">Pros</h2>
            <ul className="mt-3 space-y-2 text-emerald-900">
              {tool.pros.length > 0 ? tool.pros.map((item) => <li key={item}>- {item}</li>) : <li>- Not publicly listed</li>}
            </ul>
          </section>

          <section className="rounded-3xl border border-rose-200 bg-rose-50/40 p-6">
            <h2 className="text-xl font-bold text-rose-800">Cons</h2>
            <ul className="mt-3 space-y-2 text-rose-900">
              {tool.cons.length > 0 ? tool.cons.map((item) => <li key={item}>- {item}</li>) : <li>- Not publicly listed</li>}
            </ul>
          </section>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900">Use Cases</h3>
            <ul className="mt-3 space-y-2 text-slate-700">
              {tool.useCases.length > 0 ? tool.useCases.map((item) => <li key={item}>- {item}</li>) : <li>- Not publicly listed</li>}
            </ul>
          </section>

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900">Best For</h3>
            <ul className="mt-3 space-y-2 text-slate-700">
              {tool.bestFor.length > 0 ? tool.bestFor.map((item) => <li key={item}>- {item}</li>) : <li>- Not publicly listed</li>}
            </ul>
          </section>

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900">Not Ideal For</h3>
            <ul className="mt-3 space-y-2 text-slate-700">
              {tool.notIdealFor.length > 0 ? tool.notIdealFor.map((item) => <li key={item}>- {item}</li>) : <li>- Not publicly listed</li>}
            </ul>
          </section>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900">Features</h3>
            <ul className="mt-3 space-y-2 text-slate-700">
              {tool.features.length > 0 ? tool.features.map((item) => <li key={item}>- {item}</li>) : <li>- Not publicly listed</li>}
            </ul>
          </section>

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900">Platforms and Integrations</h3>
            <p className="mt-3 text-sm font-semibold uppercase tracking-[0.15em] text-slate-500">Platforms</p>
            <ul className="mt-2 space-y-2 text-slate-700">
              {tool.platforms.length > 0 ? tool.platforms.map((item) => <li key={item}>- {item}</li>) : <li>- Not publicly listed</li>}
            </ul>
            <p className="mt-4 text-sm font-semibold uppercase tracking-[0.15em] text-slate-500">Integrations</p>
            <ul className="mt-2 space-y-2 text-slate-700">
              {tool.integrations.length > 0 ? tool.integrations.map((item) => <li key={item}>- {item}</li>) : <li>- Not publicly listed</li>}
            </ul>
          </section>
        </div>

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
