import type { Metadata } from "next";
import Link from "next/link";

import AffiliateCTA from "@/components/AffiliateCTA";
import SchemaOrg from "@/components/SchemaOrg";

const VERIFIED_DATE = "2026-08-11";

export const metadata: Metadata = {
  title: "beehiiv vs Substack: Which Newsletter Platform Is Right for You?",
  description:
    "A side-by-side comparison of beehiiv and Substack — pricing, monetization, growth tools, and publishing features — to help you choose the right newsletter platform.",
  alternates: { canonical: "/guides/beehiiv-vs-substack" },
  openGraph: {
    title: "beehiiv vs Substack: Which Newsletter Platform Is Right for You?",
    description: "A side-by-side comparison of beehiiv and Substack to help you choose the right newsletter platform.",
    url: "/guides/beehiiv-vs-substack",
    siteName: "LeTrusto",
    type: "article",
  },
};

type CompRow = { feature: string; beehiiv: string; substack: string; edge: "beehiiv" | "substack" | "comparable" | "depends" };

const COMPARISON: CompRow[] = [
  { feature: "Free plan", beehiiv: "Yes — up to 2,500 subscribers", substack: "Yes — unlimited subscribers", edge: "substack" },
  { feature: "Custom domain", beehiiv: "Yes (all plans)", substack: "Yes (custom domain support)", edge: "comparable" },
  { feature: "Email automations", beehiiv: "Scale plan and above", substack: "Limited (welcome sequences)", edge: "beehiiv" },
  { feature: "Built-in referral program", beehiiv: "Scale plan and above", substack: "No native referral program", edge: "beehiiv" },
  { feature: "Recommendation network", beehiiv: "Yes (Launch+)", substack: "Yes (Substack Network)", edge: "comparable" },
  { feature: "Paid subscriptions", beehiiv: "Scale plan — 0% take rate", substack: "All plans — 10% platform fee", edge: "beehiiv" },
  { feature: "Native ad network", beehiiv: "Yes (Scale+)", substack: "No native ad network", edge: "beehiiv" },
  { feature: "Remove platform branding", beehiiv: "Max plan ($96/month)", substack: "Not available", edge: "beehiiv" },
  { feature: "Podcast hosting", beehiiv: "Yes (built-in)", substack: "Yes (built-in)", edge: "comparable" },
  { feature: "Community features", beehiiv: "Yes (Scale+)", substack: "Yes (Notes, Chat)", edge: "comparable" },
  { feature: "Design flexibility", beehiiv: "High — templates + custom", substack: "Limited — minimal styling", edge: "beehiiv" },
  { feature: "SEO / website builder", beehiiv: "Full website + AI builder", substack: "Publication site (limited SEO)", edge: "beehiiv" },
  { feature: "Simplicity", beehiiv: "More features = more to learn", substack: "Very simple — write and publish", edge: "substack" },
  { feature: "Built-in reader network", beehiiv: "Recommendation network", substack: "Substack app + Notes feed", edge: "substack" },
  { feature: "API access", beehiiv: "Yes (all plans)", substack: "No public API", edge: "beehiiv" },
];

const EDGE_STYLE: Record<CompRow["edge"], string> = {
  beehiiv: "text-[var(--lt-purple)] font-semibold",
  substack: "text-orange-600 font-semibold",
  comparable: "text-[var(--text-muted)]",
  depends: "text-amber-600",
};

export default function BeehiivVsSubstackGuide() {
  return (
    <main className="min-h-screen bg-[var(--surface-soft)] px-6 pb-16 pt-10">
      <SchemaOrg type="WebPage" data={{ headline: "beehiiv vs Substack: Which Newsletter Platform Is Right for You?", datePublished: "2026-08-11", author: { "@type": "Organization", name: "LeTrusto" } }} />

      <article className="mx-auto max-w-4xl space-y-10">
        <nav aria-label="Breadcrumb" className="text-xs text-[var(--text-muted)]">
          <ol className="flex flex-wrap items-center gap-1">
            <li><Link href="/" className="lt-link">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/guides" className="lt-link">Guides</Link></li>
            <li aria-hidden="true">/</li>
            <li className="font-medium text-[var(--text-primary)]">beehiiv vs Substack</li>
          </ol>
        </nav>

        <header>
          <span className="lt-badge lt-badge-brand">Comparison Guide</span>
          <h1 className="lt-heading-1 mt-3">beehiiv vs Substack: Which Newsletter Platform Is Right for You?</h1>
          <p className="lt-body mt-4 max-w-3xl">
            Both beehiiv and Substack let you publish newsletters and build an audience. But they serve
            different needs. This comparison helps you decide which platform fits your goals.
          </p>
          <p className="mt-3 text-xs text-[var(--text-muted)]">Comparison verified: {VERIFIED_DATE}</p>
        </header>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">Quick Summary</h2>
          <div className="mt-4 grid gap-6 md:grid-cols-2">
            <div className="rounded-[var(--radius-lg)] border border-[var(--lt-purple-light)] bg-[rgba(124,58,237,0.03)] p-5">
              <h3 className="lt-heading-3 text-[var(--lt-purple-dark)]">beehiiv</h3>
              <p className="lt-body-sm mt-2">A growth-focused newsletter platform with built-in monetization (ads, paid subs at 0% take rate), referral programs, automations, and website tools. More features, more control.</p>
            </div>
            <div className="rounded-[var(--radius-lg)] border border-orange-200 bg-orange-50/30 p-5">
              <h3 className="lt-heading-3 text-orange-700">Substack</h3>
              <p className="lt-body-sm mt-2">A simple publishing platform with a built-in reader network. Minimal setup, clean writing experience. Takes 10% of paid subscription revenue.</p>
            </div>
          </div>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] overflow-x-auto p-6">
          <h2 className="lt-heading-2 mb-4">Feature Comparison</h2>
          <table className="w-full min-w-[600px] text-sm">
            <thead>
              <tr className="border-b border-[var(--border)] text-left">
                <th className="pb-3 pr-4 font-semibold text-[var(--text-primary)]">Feature</th>
                <th className="pb-3 pr-4 font-semibold text-[var(--lt-purple)]">beehiiv</th>
                <th className="pb-3 pr-4 font-semibold text-orange-600">Substack</th>
                <th className="pb-3 font-semibold text-[var(--text-muted)]">Edge</th>
              </tr>
            </thead>
            <tbody>
              {COMPARISON.map((row) => (
                <tr key={row.feature} className="border-b border-[var(--surface-muted)]">
                  <td className="py-3 pr-4 font-medium text-[var(--text-primary)]">{row.feature}</td>
                  <td className="py-3 pr-4 text-[var(--text-secondary)]">{row.beehiiv}</td>
                  <td className="py-3 pr-4 text-[var(--text-secondary)]">{row.substack}</td>
                  <td className={`py-3 text-xs ${EDGE_STYLE[row.edge]}`}>
                    {row.edge === "comparable" ? "Comparable" : row.edge === "depends" ? "Depends" : row.edge}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">The Decision</h2>
          <div className="mt-4 space-y-5">
            <div>
              <h3 className="lt-heading-3 text-[var(--lt-purple-dark)]">Choose beehiiv if...</h3>
              <ul className="lt-body mt-2 space-y-1.5">
                <li>• You want to monetize via ads AND paid subscriptions without platform fees</li>
                <li>• You need email automations, referral programs, and growth tools</li>
                <li>• You want full design control and a custom website</li>
                <li>• You plan to scale a newsletter as a business</li>
              </ul>
            </div>
            <div>
              <h3 className="lt-heading-3 text-orange-700">Choose Substack if...</h3>
              <ul className="lt-body mt-2 space-y-1.5">
                <li>• You want the simplest possible publishing experience</li>
                <li>• You value Substack&apos;s built-in reader app and discovery network</li>
                <li>• You plan to monetize only through paid subscriptions (and accept the 10% fee)</li>
                <li>• You don&apos;t need advanced automation or growth tools</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] border-[var(--lt-purple-light)] bg-[rgba(124,58,237,0.03)] p-8">
          <h2 className="lt-heading-3 text-[var(--lt-purple-dark)]">LeTrusto Take</h2>
          <p className="lt-body mt-3">
            For creators who treat their newsletter as a business — needing growth tools, monetization flexibility,
            and audience ownership — beehiiv offers significantly more control. Substack wins on simplicity and its
            built-in reader network, making it a good fit for writers who primarily want to write and don&apos;t need
            complex growth infrastructure.
          </p>
        </section>

        <AffiliateCTA toolSlug="beehiiv" toolName="beehiiv" websiteUrl="https://www.beehiiv.com" />

        <footer className="flex flex-wrap gap-3 border-t border-[var(--border)] pt-8">
          <Link href="/ai-tools/beehiiv" className="lt-btn lt-btn-md lt-btn-secondary">beehiiv Profile</Link>
          <Link href="/guides/beehiiv-pricing" className="lt-btn lt-btn-md lt-btn-secondary">beehiiv Pricing</Link>
          <Link href="/guides" className="lt-btn lt-btn-md lt-btn-secondary">All Guides</Link>
        </footer>
      </article>
    </main>
  );
}
