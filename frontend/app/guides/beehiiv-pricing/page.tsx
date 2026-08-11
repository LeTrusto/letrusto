import type { Metadata } from "next";
import Link from "next/link";
import { ExternalLink } from "lucide-react";

import AffiliateCTA from "@/components/AffiliateCTA";
import SchemaOrg from "@/components/SchemaOrg";

const VERIFIED_DATE = "2026-08-11";

export const metadata: Metadata = {
  title: "beehiiv Pricing: Plans, Features & Newsletter Costs",
  description:
    "A clear breakdown of beehiiv plans — Launch (free), Scale, and Max — with guidance on which plan fits newsletter creators, publishers, and media operators.",
  alternates: { canonical: "/guides/beehiiv-pricing" },
  openGraph: {
    title: "beehiiv Pricing: Plans, Features & Newsletter Costs",
    description: "A clear breakdown of beehiiv plans with guidance on which fits newsletter creators and publishers.",
    url: "/guides/beehiiv-pricing",
    siteName: "LeTrusto",
    type: "article",
  },
};

const PLANS = [
  { name: "Launch", price: "$0/month", note: "Up to 2,500 subscribers", highlight: false, bestFor: "New creators testing the platform",
    includes: ["Unlimited email sends", "Newsletter, website, and podcast", "Recommendation network", "Custom domains", "API access", "AI Website Builder"],
    limitations: ["No email automations", "No monetization tools (ads, paid subs)", "No surveys or A/B testing", "beehiiv branding included"] },
  { name: "Scale", price: "$43/month (annual)", note: "$517 billed annually", highlight: true, bestFor: "Growing creators monetizing their audience",
    includes: ["Everything in Launch", "Ad Network access", "Paid subscriptions (0% take rate)", "Email automations", "Surveys and polls", "Community features", "3 team seats", "Human support"],
    limitations: ["beehiiv branding still present", "Limited to Scale subscriber tiers"] },
  { name: "Max", price: "$96/month (annual)", note: "$1,151 billed annually", highlight: false, bestFor: "Established publishers needing full control",
    includes: ["Everything in Scale", "Remove beehiiv branding", "Unlimited team seats", "Priority support", "Audio newsletters", "Send API", "Getty Image credits", "Up to 10 publications"],
    limitations: ["Higher cost", "Some features only relevant at scale"] },
];

export default function BeehiivPricingGuide() {
  return (
    <main className="min-h-screen bg-[var(--surface-soft)] px-6 pb-16 pt-10">
      <SchemaOrg type="WebPage" data={{ headline: "beehiiv Pricing: Plans, Features & Newsletter Costs", datePublished: "2026-08-11", author: { "@type": "Organization", name: "LeTrusto" } }} />

      <article className="mx-auto max-w-4xl space-y-10">
        <nav aria-label="Breadcrumb" className="text-xs text-[var(--text-muted)]">
          <ol className="flex flex-wrap items-center gap-1">
            <li><Link href="/" className="lt-link">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/guides" className="lt-link">Guides</Link></li>
            <li aria-hidden="true">/</li>
            <li className="font-medium text-[var(--text-primary)]">beehiiv Pricing</li>
          </ol>
        </nav>

        <header>
          <span className="lt-badge lt-badge-brand">Pricing Guide</span>
          <h1 className="lt-heading-1 mt-3">beehiiv Pricing: Plans, Features &amp; Newsletter Costs</h1>
          <p className="lt-body mt-4 max-w-3xl">
            beehiiv is a newsletter platform built for creators and media operators. It combines publishing,
            growth tools, and monetization in one place. This guide explains its pricing so you can decide which plan matches your stage.
          </p>
          <p className="mt-3 text-xs text-[var(--text-muted)]">Pricing verified: {VERIFIED_DATE} · Source: beehiiv.com/pricing</p>
        </header>

        <section className="space-y-4">
          <h2 className="lt-heading-2">Current Plans</h2>
          <div className="grid gap-6 md:grid-cols-3">
            {PLANS.map((plan) => (
              <div key={plan.name} className={`lt-card rounded-[var(--radius-2xl)] p-6 ${plan.highlight ? "border-[var(--lt-purple-light)]" : ""}`}>
                {plan.highlight && <span className="lt-badge lt-badge-brand mb-3">Most Popular</span>}
                <h3 className="lt-heading-3">{plan.name}</h3>
                <p className="mt-1 text-xl font-black text-[var(--text-primary)]">{plan.price}</p>
                <p className="text-xs text-[var(--text-muted)]">{plan.note}</p>
                <p className="lt-body-sm mt-2">{plan.bestFor}</p>
                <h4 className="lt-label mt-5 mb-2">Includes</h4>
                <ul className="space-y-1.5 text-sm text-[var(--text-secondary)]">
                  {plan.includes.map((item) => <li key={item} className="flex items-start gap-2"><span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />{item}</li>)}
                </ul>
                <h4 className="lt-label mt-4 mb-2">Limitations</h4>
                <ul className="space-y-1.5 text-sm text-[var(--text-secondary)]">
                  {plan.limitations.map((item) => <li key={item} className="flex items-start gap-2"><span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-rose-400" />{item}</li>)}
                </ul>
              </div>
            ))}
          </div>
          <p className="lt-body-sm">Enterprise plans with custom pricing are available for 100K+ subscribers. <a href="https://www.beehiiv.com/pricing" target="_blank" rel="noreferrer" className="lt-link font-semibold">View current pricing <ExternalLink className="inline h-3 w-3" /></a></p>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">Who should consider beehiiv?</h2>
          <ul className="lt-body mt-4 space-y-2">
            <li>• Newsletter creators who want publishing and growth tools in one platform</li>
            <li>• Independent publishers looking to monetize via ads, paid subscriptions, or recommendations</li>
            <li>• Media operators who need multiple publications under one account</li>
          </ul>
          <h3 className="lt-heading-3 mt-6">Who may not need beehiiv?</h3>
          <ul className="lt-body mt-3 space-y-2">
            <li>• E-commerce businesses needing transactional email and product integrations</li>
            <li>• Teams needing complex marketing automation workflows (consider Moosend or HighLevel)</li>
            <li>• Organizations that need a CRM alongside their email platform</li>
          </ul>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] border-[var(--lt-purple-light)] bg-[rgba(124,58,237,0.03)] p-8">
          <h2 className="lt-heading-3 text-[var(--lt-purple-dark)]">LeTrusto Take</h2>
          <p className="lt-body mt-3">
            beehiiv is the strongest option for newsletter-first creators who want publishing, growth, and monetization
            in one platform. The free Launch plan (up to 2,500 subscribers) makes it zero-risk to start. Scale at $43/month
            unlocks the monetization features that set beehiiv apart from general email tools.
          </p>
        </section>

        <AffiliateCTA toolSlug="beehiiv" toolName="beehiiv" websiteUrl="https://www.beehiiv.com" />

        <footer className="flex flex-wrap gap-3 border-t border-[var(--border)] pt-8">
          <Link href="/ai-tools/beehiiv" className="lt-btn lt-btn-md lt-btn-secondary">beehiiv Profile</Link>
          <Link href="/guides/beehiiv-vs-substack" className="lt-btn lt-btn-md lt-btn-secondary">beehiiv vs Substack</Link>
          <Link href="/guides" className="lt-btn lt-btn-md lt-btn-secondary">All Guides</Link>
        </footer>
      </article>
    </main>
  );
}
