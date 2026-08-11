import type { Metadata } from "next";
import Link from "next/link";
import { ExternalLink } from "lucide-react";

import AffiliateCTA from "@/components/AffiliateCTA";
import SchemaOrg from "@/components/SchemaOrg";

const VERIFIED_DATE = "2026-08-11";

export const metadata: Metadata = {
  title: "Synthesia Pricing: Plans, Features & AI Video Costs",
  description:
    "A clear breakdown of Synthesia AI video plans — Starter, Creator, and Enterprise — with guidance on which plan fits your video production needs.",
  alternates: { canonical: "/guides/synthesia-pricing" },
  openGraph: {
    title: "Synthesia Pricing: Plans, Features & AI Video Costs",
    description: "A breakdown of Synthesia AI video plans with guidance on which fits your production needs.",
    url: "/guides/synthesia-pricing",
    siteName: "LeTrusto",
    type: "article",
  },
};

export default function SynthesiaPricingGuide() {
  return (
    <main className="min-h-screen bg-[var(--surface-soft)] px-6 pb-16 pt-10">
      <SchemaOrg type="WebPage" data={{ headline: "Synthesia Pricing: Plans, Features & AI Video Costs", datePublished: "2026-08-11", author: { "@type": "Organization", name: "LeTrusto" } }} />

      <article className="mx-auto max-w-4xl space-y-10">
        <nav aria-label="Breadcrumb" className="text-xs text-[var(--text-muted)]">
          <ol className="flex flex-wrap items-center gap-1">
            <li><Link href="/" className="lt-link">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li><Link href="/guides" className="lt-link">Guides</Link></li>
            <li aria-hidden="true">/</li>
            <li className="font-medium text-[var(--text-primary)]">Synthesia Pricing</li>
          </ol>
        </nav>

        <header>
          <span className="lt-badge lt-badge-brand">Pricing Guide</span>
          <h1 className="lt-heading-1 mt-3">Synthesia Pricing: Plans, Features &amp; AI Video Costs</h1>
          <p className="lt-body mt-4 max-w-3xl">
            Synthesia is an AI video generation platform that creates professional videos from text using AI avatars.
            This guide explains its pricing structure so you can evaluate whether it fits your video production workflow and budget.
          </p>
          <p className="mt-3 text-xs text-[var(--text-muted)]">Pricing verified: {VERIFIED_DATE} · Source: synthesia.io/pricing</p>
        </header>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">What is Synthesia?</h2>
          <p className="lt-body mt-3">
            Synthesia allows you to create video content by typing a script. The platform generates video with AI avatars
            presenting your content — no cameras, studios, or actors required. It supports 140+ languages and is primarily
            used for corporate training, product explainers, and internal communications.
          </p>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">Pricing Structure</h2>
          <p className="lt-body mt-3">
            Synthesia offers Starter, Creator, and Enterprise plans. Pricing details are available on the official pricing page.
            Plans differ primarily in video minutes, avatar options, and collaboration features.
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface-soft)] p-4">
              <p className="text-sm font-bold text-[var(--text-primary)]">Starter</p>
              <p className="mt-1 text-xs text-[var(--text-muted)]">For individuals creating basic AI videos. Limited video minutes and features.</p>
            </div>
            <div className="rounded-[var(--radius-lg)] border border-[var(--lt-purple-light)] bg-[var(--surface-soft)] p-4">
              <p className="text-sm font-bold text-[var(--text-primary)]">Creator</p>
              <p className="mt-1 text-xs text-[var(--text-muted)]">More video minutes, additional avatars, and collaboration features for growing teams.</p>
            </div>
            <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface-soft)] p-4">
              <p className="text-sm font-bold text-[var(--text-primary)]">Enterprise</p>
              <p className="mt-1 text-xs text-[var(--text-muted)]">Custom avatars, SSO, dedicated support, and unlimited video creation.</p>
            </div>
          </div>
          <p className="mt-4 text-xs text-[var(--text-muted)]">
            Exact pricing may vary. <a href="https://www.synthesia.io/pricing" target="_blank" rel="noreferrer" className="lt-link font-semibold">View current pricing at synthesia.io <ExternalLink className="inline h-3 w-3" /></a>
          </p>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] p-8">
          <h2 className="lt-heading-2">Who should consider Synthesia?</h2>
          <ul className="lt-body mt-4 space-y-2">
            <li>• L&amp;D teams producing training videos at scale without video production resources</li>
            <li>• Marketing teams needing quick explainer or product demo videos</li>
            <li>• Organizations with multilingual communication needs (140+ languages)</li>
            <li>• Companies that need to update video content frequently without re-shooting</li>
          </ul>
          <h3 className="lt-heading-3 mt-6">Who may not need Synthesia?</h3>
          <ul className="lt-body mt-3 space-y-2">
            <li>• Creative agencies producing cinematic or highly-produced content</li>
            <li>• Teams needing real-time live video or streaming capabilities</li>
            <li>• Individual creators with very small video volume (free tools may suffice)</li>
          </ul>
        </section>

        <section className="lt-card rounded-[var(--radius-2xl)] border-[var(--lt-purple-light)] bg-[rgba(124,58,237,0.03)] p-8">
          <h2 className="lt-heading-3 text-[var(--lt-purple-dark)]">LeTrusto Take</h2>
          <p className="lt-body mt-3">
            Synthesia is a practical choice when you need to produce training, onboarding, or explainer videos at scale
            without the overhead of traditional video production. It shines for teams that update content frequently or
            need multilingual output. For one-off creative projects, traditional video tools may be more appropriate.
          </p>
        </section>

        <AffiliateCTA toolSlug="synthesia" toolName="Synthesia" websiteUrl="https://www.synthesia.io" />

        <footer className="flex flex-wrap gap-3 border-t border-[var(--border)] pt-8">
          <Link href="/ai-tools/synthesia" className="lt-btn lt-btn-md lt-btn-secondary">Synthesia Profile</Link>
          <Link href="/guides" className="lt-btn lt-btn-md lt-btn-secondary">All Guides</Link>
          <Link href="/compare" className="lt-btn lt-btn-md lt-btn-secondary">Compare Tools</Link>
        </footer>
      </article>
    </main>
  );
}
