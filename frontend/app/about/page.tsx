import type { Metadata } from "next";
import Link from "next/link";

import SchemaOrg from "@/components/SchemaOrg";

export const metadata: Metadata = {
  title: "About LeTrusto",
  description: "Learn how LeTrusto approaches recommendations, editorial standards, trust, privacy, and affiliate transparency.",
  alternates: {
    canonical: "/about",
  },
  openGraph: {
    title: "About LeTrusto",
    description: "Learn how LeTrusto approaches recommendations, editorial standards, trust, privacy, and affiliate transparency.",
    url: "/about",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "About LeTrusto",
    description: "Learn how LeTrusto approaches recommendations, editorial standards, trust, privacy, and affiliate transparency.",
    images: ["/images/og-default.svg"],
  },
};

export default function AboutPage() {
  const faqItems = [
    {
      q: "Does LeTrusto sell products directly?",
      a: "No. LeTrusto helps users discover, compare, and evaluate products and services before completing purchases with external partners.",
    },
    {
      q: "How are recommendations generated?",
      a: "Recommendations use structured product data, editorial review context, use-case matching, and comparison scoring tuned for practical buyer outcomes.",
    },
    {
      q: "Are affiliate links clearly disclosed?",
      a: "Yes. We disclose that some outbound links may generate commissions. That support does not change our commitment to transparent guidance.",
    },
    {
      q: "Can brands or partners influence rankings?",
      a: "Commercial relationships can create partnership opportunities, but they do not bypass recommendation quality, relevance, or trust safeguards.",
    },
    {
      q: "How do you handle corrections or reported issues?",
      a: "We review reported issues quickly, correct factual mistakes, and update guidance when new evidence materially changes a recommendation.",
    },
    {
      q: "Can enterprise partners collaborate with LeTrusto?",
      a: "Yes. We support partnership discussions around affiliate programs, trusted data integration, and category expansion initiatives.",
    },
  ];

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(168,85,247,0.12),_transparent_24%),radial-gradient(circle_at_top_right,_rgba(251,113,133,0.1),_transparent_22%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)]">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "About LeTrusto",
          url: "https://letrusto.com/about",
          description: "Learn how LeTrusto approaches recommendations, editorial standards, trust, privacy, and affiliate transparency.",
        }}
      />
      <SchemaOrg
        type="FAQPage"
        data={{
          mainEntity: faqItems.map((item) => ({
            "@type": "Question",
            name: item.q,
            acceptedAnswer: {
              "@type": "Answer",
              text: item.a,
            },
          })),
        }}
      />
      <section className="mx-auto max-w-6xl px-6 py-14 md:py-18">
        <div className="max-w-4xl">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">About LeTrusto</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950 md:text-6xl">Built to make buying decisions clearer, faster, and more trustworthy</h1>
          <p className="mt-5 max-w-3xl text-base leading-relaxed text-slate-600 md:text-lg">
            LeTrusto helps people evaluate products, services, and complex trade-offs without relying on fragmented reviews, hype cycles, or low-trust affiliate content.
          </p>
        </div>

        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {[
            { title: "Our Mission", copy: "Reduce decision fatigue by turning scattered product research into clear, actionable guidance." },
            { title: "Our Vision", copy: "Set a higher standard for trustworthy recommendation experiences across products, software, and services." },
            { title: "Core Principle", copy: "If a recommendation cannot be explained clearly, it should not be presented as trusted advice." },
          ].map((item) => (
            <article key={item.title} className="rounded-[1.75rem] border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-950">{item.title}</h2>
              <p className="mt-3 text-sm leading-relaxed text-slate-600">{item.copy}</p>
            </article>
          ))}
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-black tracking-tight text-slate-950">How LeTrusto Works</h2>
            <div className="mt-6 space-y-5 text-sm leading-7 text-slate-600">
              <p><strong className="text-slate-950">1. Intent capture:</strong> We start with user intent such as budget, priorities, use case, and risk tolerance.</p>
              <p><strong className="text-slate-950">2. Data normalization:</strong> Product and service data is standardized so options can be compared consistently across brands and models.</p>
              <p><strong className="text-slate-950">3. Scoring and trade-off analysis:</strong> We evaluate fit against practical outcomes such as reliability, value, lifecycle support, and feature relevance.</p>
              <p><strong className="text-slate-950">4. Editorial context:</strong> Recommendation outputs are supported by buyer guidance that explains when a choice is strong and when it is not.</p>
              <p><strong className="text-slate-950">5. Continuous improvement:</strong> We monitor feedback, partner data quality, and market changes to improve recommendation quality over time.</p>
            </div>
          </section>

          <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-black tracking-tight text-slate-950">Editorial Standards</h2>
            <div className="mt-6 space-y-5 text-sm leading-7 text-slate-600">
              <p>We prioritize accuracy, clarity, and practical decision value over clickbait, keyword stuffing, or speculative claims.</p>
              <p>Every recommendation should be explainable in plain language, including who it is best for and where its trade-offs appear.</p>
              <p>When evidence changes, we update guidance and maintain a correction-first posture to protect user trust.</p>
              <p>Commercial relationships cannot bypass editorial safeguards, trust checks, or recommendation integrity rules.</p>
            </div>
          </section>
        </div>

        <section className="mt-12 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-black tracking-tight text-slate-950">Recommendation Methodology</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {[
              "Fit-first scoring calibrated by category and use case.",
              "Transparent ranking logic with explainable highlights.",
              "Comparisons designed around practical trade-offs, not just specs.",
              "Quality checks for stale, biased, or incomplete signals.",
              "Ongoing refinement using feedback and conversion-quality indicators.",
              "Fallback guidance when certainty is low or data is incomplete.",
            ].map((point) => (
              <article key={point} className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-5 text-sm font-medium text-slate-700">
                {point}
              </article>
            ))}
          </div>
        </section>

        <section className="mt-12 grid gap-6 lg:grid-cols-2">
          <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-black tracking-tight text-slate-950">Affiliate Transparency</h2>
            <div className="mt-5 space-y-4 text-sm leading-7 text-slate-600">
              <p>LeTrusto may earn commissions when users click affiliate links and complete eligible purchases with partner platforms such as retailers, hosting companies, or software providers.</p>
              <p>Affiliate revenue sustains the platform and does not override evaluation logic, editorial framing, or recommendation quality safeguards.</p>
              <p>For users and partners, this means we optimize for long-term trust and outcome quality instead of short-term click volume.</p>
            </div>
          </article>
          <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-black tracking-tight text-slate-950">Why Trust LeTrusto</h2>
            <ul className="mt-5 space-y-3 text-sm leading-7 text-slate-600">
              <li className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 rounded-full bg-violet-600" aria-hidden="true" />Explainable recommendation outputs.</li>
              <li className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 rounded-full bg-violet-600" aria-hidden="true" />Decision-first UX focused on clarity and confidence.</li>
              <li className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 rounded-full bg-violet-600" aria-hidden="true" />Editorial safeguards that prioritize user outcomes.</li>
              <li className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 rounded-full bg-violet-600" aria-hidden="true" />Transparent disclosures and continuous quality improvements.</li>
            </ul>
          </article>
        </section>

        <section className="mt-12 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-black tracking-tight text-slate-950">Business Partnerships</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <article className="rounded-[1.5rem] bg-slate-50 p-5">
              <h3 className="text-lg font-bold text-slate-950">Affiliate Programs</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">Partner with LeTrusto for category-relevant, trust-first traffic and conversion quality.</p>
            </article>
            <article className="rounded-[1.5rem] bg-slate-50 p-5">
              <h3 className="text-lg font-bold text-slate-950">Data Integrations</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">Collaborate on product feeds, pricing signals, and verified information quality pipelines.</p>
            </article>
            <article className="rounded-[1.5rem] bg-slate-50 p-5">
              <h3 className="text-lg font-bold text-slate-950">Category Expansion</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">Co-build new category experiences with structured evaluation and editorial governance.</p>
            </article>
          </div>
        </section>

        <section className="mt-12 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-black tracking-tight text-slate-950">Frequently Asked Questions</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {faqItems.map((item) => (
              <article key={item.q} className="rounded-[1.25rem] bg-slate-50 p-5">
                <h3 className="text-base font-bold text-slate-950">{item.q}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{item.a}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="mt-12 rounded-[2rem] border border-slate-200 bg-slate-950 p-8 text-white shadow-sm md:p-10">
          <h2 className="text-3xl font-black tracking-tight">Contact Information</h2>
          <p className="mt-4 max-w-3xl text-sm leading-relaxed text-white/80 md:text-base">
            For editorial questions, support, affiliate approvals, partnership discussions, or product data opportunities, contact hello@letrusto.com or use the support centre.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/support" className="rounded-2xl bg-white px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-slate-100">Open support centre</Link>
            <Link href="/guides" className="rounded-2xl border border-white/20 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">Read buying guides</Link>
            <Link href="/methodology" className="rounded-2xl border border-white/20 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">Research methodology</Link>
            <Link href="/affiliate-disclosure" className="rounded-2xl border border-white/20 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">Affiliate disclosure</Link>
          </div>
        </section>
      </section>
    </main>
  );
}
