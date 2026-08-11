import type { Metadata } from "next";
import Link from "next/link";
import { ExternalLink } from "lucide-react";

import AffiliateCTA from "@/components/AffiliateCTA";
import SchemaOrg from "@/components/SchemaOrg";

const VERIFIED_DATE = "2026-08-11";

export const metadata: Metadata = {
  title: "HighLevel Pricing: Plans, Features & What You Should Know",
  description:
    "A clear breakdown of HighLevel plans — Starter and Unlimited — with guidance on which plan fits agencies, freelancers, and growing businesses.",
  alternates: { canonical: "/guides/highlevel-pricing" },
  openGraph: {
    title: "HighLevel Pricing: Plans, Features & What You Should Know",
    description: "A clear breakdown of HighLevel plans — Starter and Unlimited — with guidance on which plan fits agencies, freelancers, and growing businesses.",
    url: "/guides/highlevel-pricing",
    siteName: "LeTrusto",
    type: "article",
  },
};

const PLANS = [
  {
    name: "Starter",
    price: "$97/month",
    highlight: false,
    bestFor: "Freelancers and solo marketers getting started",
    includes: ["3 sub-accounts", "Unlimited contacts", "Unlimited users", "All core features", "24/7 support"],
    limitations: ["Limited to 3 sub-accounts", "No user/agent reporting", "No API access beyond basic"],
  },
  {
    name: "Unlimited",
    price: "$297/month",
    highlight: true,
    bestFor: "Growing agencies managing multiple clients",
    includes: ["Everything in Starter", "Unlimited sub-accounts", "User/agent reporting", "Rebill phone & email (no markup)", "Basic API access"],
    limitations: ["Higher monthly cost", "Full feature set may be overkill for solo operators"],
  },
];

export default function HighLevelPricingGuide() {
  return (
    <main className="min-h-screen bg-[var(--surface-soft)] px-6 pb-16 pt-10">
      <SchemaOrg type="WebPage" data={{ headline: "HighLevel Pricing: Plans, Features & What You Should Know", datePublished: "2026-08-11", author: { "@type": "Organization", name: "LeTrusto" } }} />

      <article className="mx-auto max-w-4xl space-y-10">
        <nav aria-label="Breadcrumb" className="text-xs text-[var(--text-muted)]">
          <ol className="flex flex-wrap items-center gap-1">
            <li><Link href="/" className="lt-link">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/guides" className="lt-link">Guides</Link></li>
            <li aria-hidden="true">/</li>
            <li className="font-medium text-[var(--text-primary)]">HighLevel Pricing</li>
          </ol>
        </nav>

        <header>
          <span className="lt-badge lt-badge-brand">Pricing Guide</span>
          <h1 className="lt-heading-1 mt-3">HighLevel Pricing: Plans, Features &amp; What You Should Know</h1>
          <p className="lt-body mt-4 max-w-3xl">
            HighLevel is an all-in-one marketing, CRM, and automation platform built for agencies and service businesses.
            This guide breaks down its pricing structure so you can decide whether it fits your budget and workflow.
          </p>
          <p className="mt-3 text-xs text-[var(--text-muted)]">Pricing verified: {VERIFIED_DATE} · Source: gohighlevel.com</p>
        </header>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">What is HighLevel?</h2>
          <p className="lt-body mt-3">
            HighLevel consolidates CRM, email/SMS marketing, funnel building, appointment scheduling, workflow automation,
            and reputation management into a single platform. It is primarily designed for marketing agencies and
            small-to-medium businesses that currently pay for multiple separate tools.
          </p>
        </section>

        <section className="space-y-4">
          <h2 className="lt-heading-2">Current Plans</h2>
          <p className="text-xs text-[var(--text-muted)]">HighLevel offers a 14-day free trial on all plans. No credit card required to start.</p>

          <div className="grid gap-6 md:grid-cols-2">
            {PLANS.map((plan) => (
              <div key={plan.name} className={`lt-card rounded-[var(--radius-2xl)] p-6 ${plan.highlight ? "border-[var(--lt-purple-light)]" : ""}`}>
                {plan.highlight && <span className="lt-badge lt-badge-brand mb-3">Most Popular</span>}
                <h3 className="lt-heading-3">{plan.name}</h3>
                <p className="mt-1 text-2xl font-black text-[var(--text-primary)]">{plan.price}</p>
                <p className="lt-body-sm mt-2">{plan.bestFor}</p>
                <h4 className="lt-label mt-5 mb-2">Includes</h4>
                <ul className="space-y-1.5 text-sm text-[var(--text-secondary)]">
                  {plan.includes.map((item) => <li key={item} className="flex items-start gap-2"><span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />{item}</li>)}
                </ul>
                <h4 className="lt-label mt-5 mb-2">Limitations</h4>
                <ul className="space-y-1.5 text-sm text-[var(--text-secondary)]">
                  {plan.limitations.map((item) => <li key={item} className="flex items-start gap-2"><span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-rose-400" />{item}</li>)}
                </ul>
              </div>
            ))}
          </div>

          <p className="lt-body-sm">
            HighLevel also offers custom Enterprise pricing for larger organizations. <a href="https://www.gohighlevel.com/pricing" target="_blank" rel="noreferrer" className="lt-link font-semibold">View official pricing <ExternalLink className="inline h-3 w-3" /></a>
          </p>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">Who should consider HighLevel?</h2>
          <ul className="lt-body mt-4 space-y-2">
            <li>• Marketing agencies managing multiple clients who want to consolidate tools</li>
            <li>• Service businesses needing CRM, scheduling, and marketing automation in one place</li>
            <li>• Teams that want to white-label a platform for their own clients</li>
          </ul>
          <h3 className="lt-heading-3 mt-6">Who may not need HighLevel?</h3>
          <ul className="lt-body mt-3 space-y-2">
            <li>• Solo creators who only need email marketing (simpler tools may be more cost-effective)</li>
            <li>• Enterprise organizations with established Salesforce or HubSpot investments</li>
            <li>• Teams that prefer best-of-breed individual tools over an all-in-one platform</li>
          </ul>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] border-[var(--lt-purple-light)] bg-[rgba(124,58,237,0.03)] p-8">
          <h2 className="lt-heading-3 text-[var(--lt-purple-dark)]">LeTrusto Take</h2>
          <p className="lt-body mt-3">
            HighLevel is well-suited for agencies and service businesses that are currently paying for 3+ separate tools
            (CRM, email, funnels, scheduling). The Starter plan at $97/month can replace a significant combined software spend.
            However, if you only need simple email marketing or have light automation needs, a more focused tool may be a better fit.
          </p>
        </section>

        <AffiliateCTA toolSlug="highlevel" toolName="HighLevel" websiteUrl="https://www.gohighlevel.com" />

        <footer className="flex flex-wrap gap-3 border-t border-[var(--border)] pt-8">
          <Link href="/ai-tools/highlevel" className="lt-btn lt-btn-md lt-btn-secondary">HighLevel Profile</Link>
          <Link href="/guides" className="lt-btn lt-btn-md lt-btn-secondary">All Guides</Link>
          <Link href="/compare" className="lt-btn lt-btn-md lt-btn-secondary">Compare Tools</Link>
        </footer>
      </article>
    </main>
  );
}
