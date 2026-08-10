import type { Metadata } from "next";
import Link from "next/link";
import SchemaOrg from "@/components/SchemaOrg";

export const metadata: Metadata = {
  title: "Research & Editorial Methodology",
  description:
    "How LeTrusto sources, evaluates, verifies, and updates information about software tools and digital products.",
  alternates: {
    canonical: "/methodology",
  },
  openGraph: {
    title: "Research & Editorial Methodology | LeTrusto",
    description:
      "How LeTrusto sources, evaluates, verifies, and scores software tools to produce trustworthy buying guidance.",
    url: "/methodology",
    siteName: "LeTrusto",
    type: "website",
  },
};

const EVALUATION_CRITERIA = [
  {
    title: "Pricing verification",
    body: "We verify pricing by checking official provider pricing pages. We record the pricing model (free, freemium, monthly, annual, usage-based), entry price, and trial availability. Because software pricing changes frequently, we include a last-verified date and link to the provider's pricing page where available.",
  },
  {
    title: "Feature verification",
    body: "Features are sourced from official product documentation, provider websites, and publicly available changelogs. We do not invent features or capabilities. Where a feature is disputed or unverifiable, it is either excluded or marked as unverified.",
  },
  {
    title: "Platform availability",
    body: "We document which platforms each tool supports (web, desktop, mobile, API) based on information published by the provider. This may not reflect experimental or beta offerings.",
  },
  {
    title: "Integrations",
    body: "Integration data is based on publicly documented connections on official integration pages, marketplaces, or changelogs. We note where integration depth is limited or requires third-party connectors.",
  },
  {
    title: "Use-case fit",
    body: "Use cases are derived from the provider's own positioning, user documentation, and observable feature sets. LeTrusto does not conduct independent software testing. We aim to reflect the realistic scope of each tool.",
  },
  {
    title: "Strengths and limitations",
    body: "Pros and cons are sourced from a combination of provider documentation, published product constraints, publicly available user feedback patterns, and editorial analysis. Unverifiable claims are excluded.",
  },
  {
    title: "Recommendation scoring",
    body: "LeTrusto generates recommendation scores based on structured data including pricing model, feature completeness for the category, platform availability, use-case relevance, and editorial assessment. The scoring is deterministic and based on verified data fields, not subjective opinion.",
  },
];

export default function MethodologyPage() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(168,85,247,0.08),_transparent_30%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)]">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "Research & Editorial Methodology",
          url: "https://letrusto.com/methodology",
          description:
            "How LeTrusto sources, evaluates, verifies, and scores software tools.",
        }}
      />

      <div className="mx-auto max-w-4xl px-6 py-14">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
          How we work
        </p>
        <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
          Research &amp; Editorial Methodology
        </h1>
        <p className="mt-5 max-w-3xl text-base leading-relaxed text-slate-600">
          LeTrusto exists to help people make more confident software decisions.
          This page explains how we source data, what we verify, how
          recommendations are produced, and what our limitations are.
        </p>

        {/* Overview */}
        <section className="mt-12 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-black tracking-tight text-slate-950">
            Our approach
          </h2>
          <div className="mt-5 space-y-4 text-sm leading-7 text-slate-600">
            <p>
              LeTrusto is a research-backed platform for software comparison and
              buying guidance. We focus specifically on AI tools, business
              software, and developer tools. Our goal is to provide structured,
              verifiable information that helps users evaluate tools before
              paying for them.
            </p>
            <p>
              We do not conduct independent performance benchmarks or lab
              testing. Our evaluation is based on publicly available information
              from providers, official documentation, and structured editorial
              analysis of what a tool does and who it is for.
            </p>
            <p>
              Every data point is associated with a provenance source and a
              last-verified date. When we cannot verify a claim, we do not
              publish it.
            </p>
          </div>
        </section>

        {/* Evaluation criteria */}
        <section className="mt-8">
          <h2 className="text-2xl font-black tracking-tight text-slate-950">
            Evaluation criteria
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">
            Each tool in the LeTrusto catalog is evaluated across these
            dimensions:
          </p>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {EVALUATION_CRITERIA.map((item) => (
              <article
                key={item.title}
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
              >
                <h3 className="text-base font-bold text-slate-950">
                  {item.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {item.body}
                </p>
              </article>
            ))}
          </div>
        </section>

        {/* Provenance */}
        <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-black tracking-tight text-slate-950">
            Provenance and source verification
          </h2>
          <div className="mt-5 space-y-4 text-sm leading-7 text-slate-600">
            <p>
              All factual claims in the tool catalog are tracked with a source.
              Our provenance system records where each data point originates,
              the source URL, and the date it was last verified.
            </p>
            <p>
              Sources are classified by type: official provider page, official
              documentation, official pricing page, public changelog, or
              editorial assessment. User-generated content, affiliate blogs, and
              anonymous review aggregators are not considered primary sources.
            </p>
            <p>
              When a primary source changes, the relevant data is flagged for
              update. Users can see the last-verified date on each tool profile
              page.
            </p>
          </div>
        </section>

        {/* Freshness */}
        <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-black tracking-tight text-slate-950">
            Freshness and updates
          </h2>
          <div className="mt-5 space-y-4 text-sm leading-7 text-slate-600">
            <p>
              Software changes frequently. Pricing, features, availability, and
              supported integrations can change without notice.
            </p>
            <p>
              LeTrusto updates catalog data periodically. We include a
              last-verified date on tool profiles so you can assess how recent
              the information is. For time-sensitive purchasing decisions, always
              verify the current pricing and terms directly with the provider.
            </p>
            <p>
              If you find information that is out of date or inaccurate, please{" "}
              <Link
                href="/report-issue"
                className="font-medium text-purple-700 underline underline-offset-2 hover:text-purple-900"
              >
                report it
              </Link>
              . We review and correct reported issues promptly.
            </p>
          </div>
        </section>

        {/* Affiliate relationship */}
        <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-black tracking-tight text-slate-950">
            Affiliate relationships and editorial independence
          </h2>
          <div className="mt-5 space-y-4 text-sm leading-7 text-slate-600">
            <p>
              LeTrusto participates in affiliate programs with select software
              providers. When you purchase through an affiliate link on this
              site, we may earn a commission at no additional cost to you.
            </p>
            <p>
              Affiliate status does not determine whether a tool is listed,
              recommended, or ranked. Tools are added to the catalog when they
              meet research and relevance criteria, regardless of affiliate
              status. Scoring is driven by verified data, not by commercial
              relationships.
            </p>
            <p>
              For full details, see our{" "}
              <Link
                href="/affiliate-disclosure"
                className="font-medium text-purple-700 underline underline-offset-2 hover:text-purple-900"
              >
                Affiliate Disclosure
              </Link>
              .
            </p>
          </div>
        </section>

        {/* Limitations */}
        <section className="mt-8 rounded-3xl border border-amber-200 bg-amber-50/50 p-8">
          <h2 className="text-2xl font-black tracking-tight text-slate-950">
            Important limitations
          </h2>
          <ul className="mt-5 space-y-3 text-sm leading-7 text-slate-700">
            {[
              "We do not conduct independent performance testing, speed benchmarks, or security audits.",
              "Pricing information may not reflect regional pricing, promotional discounts, or enterprise agreements.",
              "Feature availability may differ between plan tiers not reflected in catalog data.",
              "LeTrusto does not verify claims made in user testimonials or external reviews.",
              "Recommendation scores are based on structured data and editorial weighting, not real-world user outcomes.",
              "Information on this site should inform, not replace, your own due diligence before purchasing.",
            ].map((limitation) => (
              <li key={limitation} className="flex items-start gap-3">
                <span
                  className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-amber-600"
                  aria-hidden="true"
                />
                {limitation}
              </li>
            ))}
          </ul>
        </section>

        {/* CTA */}
        <div className="mt-10 flex flex-wrap items-center gap-4">
          <Link
            href="/ai-tools"
            className="rounded-2xl bg-slate-900 px-6 py-3 text-sm font-bold text-white transition hover:bg-slate-800"
          >
            Browse AI tools
          </Link>
          <Link
            href="/about"
            className="rounded-2xl border border-slate-300 px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-500"
          >
            About LeTrusto
          </Link>
          <Link
            href="/report-issue"
            className="text-sm font-medium text-purple-700 underline underline-offset-2 hover:text-purple-900"
          >
            Report inaccurate data
          </Link>
        </div>

        <p className="mt-8 text-xs text-slate-400">Last updated: 2026-08-10</p>
      </div>
    </main>
  );
}
