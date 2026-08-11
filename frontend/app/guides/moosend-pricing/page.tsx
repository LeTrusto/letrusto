import type { Metadata } from "next";
import Link from "next/link";
import { ExternalLink } from "lucide-react";

import AffiliateCTA from "@/components/AffiliateCTA";
import SchemaOrg from "@/components/SchemaOrg";

const VERIFIED_DATE = "2026-08-11";

export const metadata: Metadata = {
  title: "Moosend Pricing: Plans, Features & Who It Is For",
  description:
    "A clear breakdown of Moosend email marketing plans — Pro, Moosend+, and Enterprise — with guidance on which plan fits your subscriber count and needs.",
  alternates: { canonical: "/guides/moosend-pricing" },
  openGraph: {
    title: "Moosend Pricing: Plans, Features & Who It Is For",
    description: "A clear breakdown of Moosend email marketing plans with guidance on which plan fits your needs.",
    url: "/guides/moosend-pricing",
    siteName: "LeTrusto",
    type: "article",
  },
};

export default function MoosendPricingGuide() {
  return (
    <main className="min-h-screen bg-[var(--surface-soft)] px-6 pb-16 pt-10">
      <SchemaOrg type="WebPage" data={{ headline: "Moosend Pricing: Plans, Features & Who It Is For", datePublished: "2026-08-11", author: { "@type": "Organization", name: "LeTrusto" } }} />

      <article className="mx-auto max-w-4xl space-y-10">
        <nav aria-label="Breadcrumb" className="text-xs text-[var(--text-muted)]">
          <ol className="flex flex-wrap items-center gap-1">
            <li><Link href="/" className="lt-link">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/guides" className="lt-link">Guides</Link></li>
            <li aria-hidden="true">/</li>
            <li className="font-medium text-[var(--text-primary)]">Moosend Pricing</li>
          </ol>
        </nav>

        <header>
          <span className="lt-badge lt-badge-brand">Pricing Guide</span>
          <h1 className="lt-heading-1 mt-3">Moosend Pricing: Plans, Features &amp; Who It Is For</h1>
          <p className="lt-body mt-4 max-w-3xl">
            Moosend is an email marketing and automation platform with drag-and-drop campaign building,
            landing pages, and audience segmentation. This guide explains its pricing model so you can
            decide whether it fits your email marketing needs and budget.
          </p>
          <p className="mt-3 text-xs text-[var(--text-muted)]">Pricing verified: {VERIFIED_DATE} · Source: moosend.com/pricing</p>
        </header>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">How Moosend Pricing Works</h2>
          <p className="lt-body mt-3">
            Moosend uses subscriber-based pricing. Your cost depends on the number of contacts in your account.
            All paid plans include unlimited email sends. Moosend also offers a pay-as-you-go credits option for occasional senders.
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface-soft)] p-4">
              <p className="text-sm font-bold text-[var(--text-primary)]">30-Day Free Trial</p>
              <p className="mt-1 text-xs text-[var(--text-muted)]">No credit card required. Up to 1,000 contacts.</p>
            </div>
            <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface-soft)] p-4">
              <p className="text-sm font-bold text-[var(--text-primary)]">Pro Plan</p>
              <p className="mt-1 text-xs text-[var(--text-muted)]">From $9/month (500 contacts). Scales with list size.</p>
            </div>
            <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface-soft)] p-4">
              <p className="text-sm font-bold text-[var(--text-primary)]">Annual Discount</p>
              <p className="mt-1 text-xs text-[var(--text-muted)]">Save 20% with annual billing. 15% on bi-annual.</p>
            </div>
          </div>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">Plan Comparison</h2>
          <div className="mt-4 space-y-4">
            <div className="rounded-[var(--radius-lg)] border border-[var(--border)] p-5">
              <h3 className="lt-heading-3">Pro</h3>
              <p className="mt-1 text-lg font-bold text-[var(--text-primary)]">From $9/month (500 contacts)</p>
              <p className="lt-body-sm mt-2">Full email marketing suite including automation workflows, landing pages, subscription forms, A/B testing, and real-time analytics. Unlimited email sends. 5 team members.</p>
            </div>
            <div className="rounded-[var(--radius-lg)] border border-[var(--border)] p-5">
              <h3 className="lt-heading-3">Moosend+</h3>
              <p className="mt-1 text-lg font-bold text-[var(--text-primary)]">Custom pricing</p>
              <p className="lt-body-sm mt-2">Everything in Pro plus transactional emails, dedicated IP, SSO &amp; SAML, custom reports, account manager, and additional enterprise add-ons. Tailored to your business needs.</p>
            </div>
            <div className="rounded-[var(--radius-lg)] border border-[var(--border)] p-5">
              <h3 className="lt-heading-3">Enterprise</h3>
              <p className="mt-1 text-lg font-bold text-[var(--text-primary)]">Custom pricing</p>
              <p className="lt-body-sm mt-2">For large organizations needing SLA, priority support, deliverability optimization, and 10+ team members.</p>
            </div>
          </div>
          <p className="mt-4 text-xs text-[var(--text-muted)]">
            Pricing scales with subscriber count. Nonprofits receive 25% off. <a href="https://moosend.com/pricing/" target="_blank" rel="noreferrer" className="lt-link font-semibold">View current pricing <ExternalLink className="inline h-3 w-3" /></a>
          </p>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">Who should consider Moosend?</h2>
          <ul className="lt-body mt-4 space-y-2">
            <li>• Small-to-medium businesses focused on email marketing and automation</li>
            <li>• Teams that want unlimited sends without per-email charges</li>
            <li>• Newsletter operators needing landing pages and forms included</li>
            <li>• Businesses looking for a Mailchimp alternative at a lower price point</li>
          </ul>
          <h3 className="lt-heading-3 mt-6">Who may not need Moosend?</h3>
          <ul className="lt-body mt-3 space-y-2">
            <li>• Enterprises needing a full CRM suite alongside email</li>
            <li>• Teams requiring deep third-party integrations beyond email workflows</li>
            <li>• Newsletter creators who want built-in monetization tools (consider beehiiv instead)</li>
          </ul>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] border-[var(--lt-purple-light)] bg-[rgba(124,58,237,0.03)] p-8">
          <h2 className="lt-heading-3 text-[var(--lt-purple-dark)]">LeTrusto Take</h2>
          <p className="lt-body mt-3">
            Moosend offers a clean email marketing experience with automation and landing pages at a competitive price.
            The 30-day free trial (no credit card) makes it low-risk to evaluate. If email marketing and automation are
            your primary needs — without requiring a full CRM — Moosend is worth considering, especially for lists under 10,000 subscribers.
          </p>
        </section>

        <AffiliateCTA toolSlug="moosend" toolName="Moosend" websiteUrl="https://moosend.com" />

        <footer className="flex flex-wrap gap-3 border-t border-[var(--border)] pt-8">
          <Link href="/ai-tools/moosend" className="lt-btn lt-btn-md lt-btn-secondary">Moosend Profile</Link>
          <Link href="/guides" className="lt-btn lt-btn-md lt-btn-secondary">All Guides</Link>
          <Link href="/compare" className="lt-btn lt-btn-md lt-btn-secondary">Compare Tools</Link>
        </footer>
      </article>
    </main>
  );
}
