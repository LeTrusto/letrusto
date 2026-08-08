import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import Script from "next/script";

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
      <main className="min-h-screen bg-slate-50 px-6 py-16">
        <div className="mx-auto max-w-4xl rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-sm">
          <h1 className="text-3xl font-black text-slate-900">AI Tool Not Found</h1>
          <p className="mt-3 text-slate-600">This tool is unavailable or not currently published.</p>
          <Link
            href="/ai-tools"
            className="mt-6 inline-flex rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
          >
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
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(186,230,253,0.2),_transparent_25%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)] px-6 py-12">
      <Script id="ai-tool-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />

      <div className="mx-auto max-w-6xl space-y-8">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{tool.category.name}</p>
              <h1 className="mt-2 text-4xl font-black tracking-tight text-slate-950">{tool.name}</h1>
              <p className="mt-2 text-lg text-slate-600">Provider: {tool.provider}</p>
              <p className="mt-4 max-w-3xl text-slate-700">{tool.description}</p>
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
              <span key={tag} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
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

        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-center gap-3">
            <a
              href={tool.websiteUrl}
              target="_blank"
              rel="noreferrer"
              className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
            >
              Visit Official Website
            </a>

            {tool.affiliateAvailable && tool.affiliateUrl ? (
              <a
                href={tool.affiliateUrl}
                target="_blank"
                rel="noreferrer"
                className="rounded-xl border border-sky-300 bg-sky-50 px-5 py-3 text-sm font-semibold text-sky-700 hover:border-sky-500"
              >
                Open Affiliate Offer
              </a>
            ) : null}

            <Link href="/ai-tools" className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 hover:border-slate-500">
              Back to AI Tools
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
