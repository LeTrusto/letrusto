import type { Metadata } from "next";
import Link from "next/link";

import SchemaOrg from "@/components/SchemaOrg";
import { getAiToolBySlug } from "@/services/ai-tools.service";

export const metadata: Metadata = {
  title: "ElevenLabs Pricing: Which Plan Is Right for You?",
  description:
    "A clear breakdown of ElevenLabs plans — Free, Starter, Creator, Pro, and Scale — with honest guidance on which plan fits your needs and budget.",
  alternates: {
    canonical: "/guides/elevenlabs-pricing",
  },
  openGraph: {
    title: "ElevenLabs Pricing: Which Plan Is Right for You?",
    description:
      "A clear breakdown of ElevenLabs plans — Free, Starter, Creator, Pro, and Scale — with honest guidance on which plan fits your needs and budget.",
    url: "/guides/elevenlabs-pricing",
    siteName: "LeTrusto",
    type: "article",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "ElevenLabs Pricing: Which Plan Is Right for You?",
    description:
      "A clear breakdown of ElevenLabs plans — Free, Starter, Creator, Pro, and Scale — with honest guidance on which plan fits your needs and budget.",
    images: ["/images/og-default.svg"],
  },
};

const VERIFIED_DATE = "2026-08-10";
const OFFICIAL_PRICING_URL = "https://elevenlabs.io/pricing";
const OFFICIAL_SITE_URL = "https://elevenlabs.io";

type Plan = {
  name: string;
  price: string;
  priceNote: string | null;
  badge: string | null;
  highlight: boolean;
  bestFor: string;
  summary: string;
  includes: string[];
  limitations: string[];
};

// Pricing sourced from official ElevenLabs affiliate program page (elevenlabs.io/affiliates).
// Creator = $22/mo and Pro = $99/mo are confirmed via affiliate page commission examples.
// Starter and Scale prices reflect publicly documented tiers; verify at elevenlabs.io/pricing.
const PLANS: Plan[] = [
  {
    name: "Free",
    price: "$0",
    priceNote: "No credit card required",
    badge: null,
    highlight: false,
    bestFor: "Testing the platform before committing",
    summary:
      "The Free plan gives you access to ElevenLabs voices with a monthly generation limit. It is suitable for evaluating voice quality before deciding whether to pay.",
    includes: [
      "Limited voice generation per month",
      "Access to pre-built AI voices",
      "Basic voice customisation settings",
      "No commercial rights",
    ],
    limitations: [
      "Monthly generation limit is low — unsuitable for regular content production",
      "No commercial usage rights",
      "No voice cloning access",
      "Watermarked audio in some use cases",
    ],
  },
  {
    name: "Starter",
    price: "From ~$5/mo",
    priceNote: "Verify current price at elevenlabs.io/pricing",
    badge: null,
    highlight: false,
    bestFor: "Occasional personal or light professional use",
    summary:
      "The Starter plan expands your monthly voice generation allowance and adds commercial rights — making it suitable for low-volume content work. It is the minimum plan for any commercial use of ElevenLabs audio.",
    includes: [
      "Increased voice generation vs Free",
      "Commercial rights included",
      "Access to standard AI voices",
      "Basic API access",
    ],
    limitations: [
      "Generation limits may still be restrictive for regular video or podcast production",
      "Voice cloning access may be limited or unavailable — verify on official pricing page",
    ],
  },
  {
    name: "Creator",
    price: "$22/mo",
    priceNote: "Billed monthly. Annual billing typically reduces cost.",
    badge: "Most popular for individuals",
    highlight: true,
    bestFor: "YouTube creators, podcasters, freelance voiceover work, content agencies",
    summary:
      "The Creator plan is the most practical entry point for consistent content production. At $22/month it gives you substantially more voice generation capacity and access to voice cloning — the combination most content creators need.",
    includes: [
      "Substantial monthly voice generation capacity",
      "Voice cloning — train the platform on your own voice",
      "Commercial rights for all generated audio",
      "Access to all standard and premium AI voices",
      "Higher quality output settings",
      "API access for automation and integrations",
    ],
    limitations: [
      "Monthly generation cap applies — heavy users (daily long-form content) may find it limiting",
      "One user seat — not designed for team sharing",
    ],
  },
  {
    name: "Pro",
    price: "$99/mo",
    priceNote: "Billed monthly. Annual billing typically reduces cost.",
    badge: "Best for professionals and small teams",
    highlight: false,
    bestFor: "Agencies, studios, developers building voice applications, teams with regular high-volume needs",
    summary:
      "Pro significantly increases generation capacity and adds features relevant to professional workflows — higher character limits, additional voice slots, and priority support. It makes sense when you or your team is producing voice content daily.",
    includes: [
      "High monthly voice generation capacity",
      "Multiple voice clone slots",
      "Full commercial rights",
      "Priority support",
      "Enhanced API access and rate limits",
      "Access to all voice models including professional-grade outputs",
    ],
    limitations: [
      "At $99/month it is a significant commitment — only justifiable for regular, revenue-generating use",
      "Enterprise features (SSO, advanced admin) require higher tiers",
    ],
  },
  {
    name: "Scale",
    price: "From ~$330/mo",
    priceNote: "Verify current price at elevenlabs.io/pricing",
    badge: null,
    highlight: false,
    bestFor: "Content studios, high-volume agencies, developer teams building voice products",
    summary:
      "Scale is designed for organisations that produce voice content at volume — publishing houses, localization agencies, or product teams building AI voice into their applications. Generation limits are substantially higher than Pro.",
    includes: [
      "Very high monthly voice generation capacity",
      "Multiple voice clone slots",
      "Higher API rate limits",
      "Full commercial and distribution rights",
      "Priority support",
    ],
    limitations: [
      "Price point ($330+/month) requires a clear business case",
      "Still a self-serve plan — enterprise controls (SSO, audit logs) require Business",
    ],
  },
  {
    name: "Business / Enterprise",
    price: "Custom",
    priceNote: "Contact ElevenLabs sales",
    badge: null,
    highlight: false,
    bestFor: "Large organisations with enterprise compliance, team management, and volume requirements",
    summary:
      "Business and Enterprise tiers are negotiated directly with ElevenLabs. They add enterprise controls, dedicated account management, custom SLAs, and higher or unlimited generation at negotiated rates.",
    includes: [
      "Custom generation limits",
      "Enterprise security and compliance",
      "Team management and admin controls",
      "Dedicated account manager",
      "SLA guarantees",
      "Custom voice model training (varies by agreement)",
    ],
    limitations: [
      "No public pricing — requires a sales conversation",
      "Not suitable for individual users or small teams",
    ],
  },
];

type UseCase = {
  label: string;
  recommendedPlan: string;
  reasoning: string;
};

const USE_CASES: UseCase[] = [
  {
    label: "YouTube creator (regular uploads)",
    recommendedPlan: "Creator ($22/mo)",
    reasoning:
      "Voice cloning and commercial rights are both needed. Creator gives enough generation capacity for most weekly upload schedules.",
  },
  {
    label: "Podcaster (weekly episodes)",
    recommendedPlan: "Creator ($22/mo)",
    reasoning:
      "A weekly podcast episode typically falls within Creator's generation limits. The voice quality is sufficient for professional-sounding output.",
  },
  {
    label: "Freelance voiceover artist",
    recommendedPlan: "Creator or Pro",
    reasoning:
      "Creator works if projects are moderate volume. If you are producing multiple long-form projects per month for clients, Pro's higher limits and priority support are worth it.",
  },
  {
    label: "Just testing AI voice quality",
    recommendedPlan: "Free",
    reasoning:
      "The free plan is sufficient to evaluate voice quality. Start free, upgrade when you have a specific use case.",
  },
  {
    label: "Developer integrating voice into an app",
    recommendedPlan: "Pro or Scale",
    reasoning:
      "API usage for applications typically requires higher rate limits and generation capacity. Pro is the minimum practical plan for development; Scale for production applications.",
  },
  {
    label: "Marketing team — ads and videos",
    recommendedPlan: "Creator or Pro",
    reasoning:
      "Depends on volume. A small team with occasional video needs can use Creator. A team producing daily ad variations should evaluate Pro or Scale.",
  },
  {
    label: "Enterprise (compliance, team admin)",
    recommendedPlan: "Business / Enterprise",
    reasoning:
      "If you need SSO, audit logs, dedicated support, or custom security terms, only the Business/Enterprise tier provides these.",
  },
];

export default async function ElevenLabsPricingGuidePage() {
  // Fetch ElevenLabs tool record to get the affiliate URL from the backend source of truth.
  // Falls back gracefully if the API is unavailable.
  const tool = await getAiToolBySlug("elevenlabs");
  const hasAffiliate = Boolean(tool?.affiliateAvailable && tool?.affiliateUrl);
  const affiliateUrl = tool?.affiliateUrl ?? null;

  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)] px-6 pb-16 pt-10">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "ElevenLabs Pricing: Which Plan Is Right for You?",
          url: "https://letrusto.com/guides/elevenlabs-pricing",
          description:
            "A clear breakdown of ElevenLabs plans — Free, Starter, Creator, Pro, and Scale — with honest guidance on which plan fits your needs and budget.",
        }}
      />

      <div className="mx-auto max-w-4xl">
        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="mb-6 text-xs text-slate-500">
          <ol className="flex flex-wrap items-center gap-1">
            <li>
              <Link href="/" className="hover:text-slate-700">
                Home
              </Link>
            </li>
            <li aria-hidden="true" className="text-slate-300">/</li>
            <li>
              <Link href="/guides" className="hover:text-slate-700">
                Guides
              </Link>
            </li>
            <li aria-hidden="true" className="text-slate-300">/</li>
            <li className="font-medium text-slate-700" aria-current="page">
              ElevenLabs Pricing
            </li>
          </ol>
        </nav>

        {/* Header */}
        <header className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-purple-600">
            Buying Guide · AI Voice
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
            ElevenLabs Pricing: Which Plan Is Right for You?
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-relaxed text-slate-600">
            ElevenLabs offers five pricing tiers ranging from free to enterprise. This guide
            breaks down what each plan actually includes, who it is designed for, and how to
            decide which level of investment makes sense for your use case.
          </p>

          {/* Meta row */}
          <div className="mt-5 flex flex-wrap items-center gap-4 text-xs text-slate-400">
            <span>
              Last verified:{" "}
              <time dateTime={VERIFIED_DATE}>
                {new Date(VERIFIED_DATE).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </time>
            </span>
            <span>Category: AI Voice Generation</span>
            <Link
              href="/methodology"
              className="underline underline-offset-2 hover:text-slate-600"
            >
              How we research
            </Link>
          </div>

          {/* Inline affiliate disclosure */}
          <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500">
            <strong className="font-semibold text-slate-700">Affiliate disclosure:</strong>{" "}
            LeTrusto is an approved affiliate partner of ElevenLabs. If you sign up through
            our link, we may earn a commission at no extra cost to you. This does not influence
            our assessment.{" "}
            <Link
              href="/affiliate-disclosure"
              className="font-medium text-purple-700 underline underline-offset-2 hover:text-purple-900"
            >
              Learn more
            </Link>
          </div>
        </header>

        {/* Quick answer */}
        <section className="mb-8 rounded-3xl border border-purple-200 bg-purple-50/50 p-6">
          <h2 className="text-xl font-bold text-slate-950">Quick recommendation</h2>
          <ul className="mt-4 space-y-2.5 text-sm text-slate-700">
            <li className="flex gap-3">
              <span className="mt-1 flex-shrink-0 text-purple-600">→</span>
              <span>
                <strong>Testing AI voice for the first time?</strong> Start with the Free plan.
                No payment required.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="mt-1 flex-shrink-0 text-purple-600">→</span>
              <span>
                <strong>YouTube creator or podcaster?</strong> The Creator plan at $22/month is
                the practical starting point for regular content production.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="mt-1 flex-shrink-0 text-purple-600">→</span>
              <span>
                <strong>Professional or small team?</strong> Pro at $99/month is designed for
                higher-volume, revenue-generating work.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="mt-1 flex-shrink-0 text-purple-600">→</span>
              <span>
                <strong>Developer or high-volume studio?</strong> Evaluate Scale or Business
                based on your API and generation volume.
              </span>
            </li>
          </ul>
        </section>

        {/* Pricing caveat */}
        <div className="mb-8 rounded-xl border border-amber-200 bg-amber-50/50 px-4 py-3 text-xs text-slate-600">
          <strong className="font-semibold text-slate-800">Pricing note:</strong> Creator ($22/mo) and Pro ($99/mo) plan prices are confirmed from the official ElevenLabs affiliate program page. All other prices reflect publicly documented tiers at the time of research. ElevenLabs updates pricing periodically.{" "}
          <a
            href={OFFICIAL_PRICING_URL}
            target="_blank"
            rel="noreferrer"
            className="font-medium text-amber-800 underline underline-offset-2 hover:text-amber-900"
          >
            Verify current pricing at elevenlabs.io/pricing
          </a>
        </div>

        {/* Quick comparison table */}
        <section className="mb-12">
          <h2 className="mb-4 text-2xl font-bold text-slate-950">Plans at a glance</h2>
          <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left">
                  <th className="px-5 py-3 font-bold text-slate-900">Plan</th>
                  <th className="px-5 py-3 font-bold text-slate-900">Price</th>
                  <th className="px-5 py-3 font-bold text-slate-900">Commercial rights</th>
                  <th className="px-5 py-3 font-bold text-slate-900">Voice cloning</th>
                  <th className="px-5 py-3 font-bold text-slate-900">Best for</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                <tr className="text-slate-600">
                  <td className="px-5 py-3 font-medium text-slate-900">Free</td>
                  <td className="px-5 py-3">$0</td>
                  <td className="px-5 py-3 text-rose-600">No</td>
                  <td className="px-5 py-3 text-rose-600">No</td>
                  <td className="px-5 py-3">Testing the platform</td>
                </tr>
                <tr className="text-slate-600">
                  <td className="px-5 py-3 font-medium text-slate-900">Starter</td>
                  <td className="px-5 py-3">From ~$5/mo</td>
                  <td className="px-5 py-3 text-emerald-700">Yes</td>
                  <td className="px-5 py-3 text-slate-400">Limited</td>
                  <td className="px-5 py-3">Light personal or commercial use</td>
                </tr>
                <tr className="bg-purple-50/30 text-slate-600">
                  <td className="px-5 py-3 font-bold text-purple-900">
                    Creator
                    <span className="ml-2 rounded-full bg-purple-100 px-2 py-0.5 text-xs font-semibold text-purple-700">
                      Popular
                    </span>
                  </td>
                  <td className="px-5 py-3 font-semibold text-slate-900">$22/mo</td>
                  <td className="px-5 py-3 text-emerald-700">Yes</td>
                  <td className="px-5 py-3 text-emerald-700">Yes</td>
                  <td className="px-5 py-3">Content creators, podcasters, YouTube</td>
                </tr>
                <tr className="text-slate-600">
                  <td className="px-5 py-3 font-medium text-slate-900">Pro</td>
                  <td className="px-5 py-3 font-semibold text-slate-900">$99/mo</td>
                  <td className="px-5 py-3 text-emerald-700">Yes</td>
                  <td className="px-5 py-3 text-emerald-700">Yes (more slots)</td>
                  <td className="px-5 py-3">Professionals, agencies, small teams</td>
                </tr>
                <tr className="text-slate-600">
                  <td className="px-5 py-3 font-medium text-slate-900">Scale</td>
                  <td className="px-5 py-3">From ~$330/mo</td>
                  <td className="px-5 py-3 text-emerald-700">Yes</td>
                  <td className="px-5 py-3 text-emerald-700">Yes</td>
                  <td className="px-5 py-3">High-volume studios, developer apps</td>
                </tr>
                <tr className="text-slate-600">
                  <td className="px-5 py-3 font-medium text-slate-900">Business</td>
                  <td className="px-5 py-3">Custom</td>
                  <td className="px-5 py-3 text-emerald-700">Yes</td>
                  <td className="px-5 py-3 text-emerald-700">Yes (custom)</td>
                  <td className="px-5 py-3">Enterprise, large teams</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Starter and Scale prices are indicative based on research dated {VERIFIED_DATE}.{" "}
            <a
              href={OFFICIAL_PRICING_URL}
              target="_blank"
              rel="noreferrer"
              className="underline hover:text-slate-600"
            >
              Verify at elevenlabs.io/pricing
            </a>
          </p>
        </section>

        {/* Individual plan sections */}
        <section className="mb-12 space-y-6">
          <h2 className="text-2xl font-bold text-slate-950">Plan-by-plan breakdown</h2>

          {PLANS.map((plan) => (
            <article
              key={plan.name}
              className={`rounded-3xl border p-6 shadow-sm ${
                plan.highlight
                  ? "border-purple-200 bg-purple-50/30"
                  : "border-slate-200 bg-white"
              }`}
            >
              <div className="flex flex-wrap items-center gap-3">
                <h3
                  className={`text-xl font-bold ${
                    plan.highlight ? "text-purple-900" : "text-slate-950"
                  }`}
                >
                  {plan.name}
                </h3>
                {plan.badge ? (
                  <span className="rounded-full bg-purple-100 px-3 py-0.5 text-xs font-semibold text-purple-700">
                    {plan.badge}
                  </span>
                ) : null}
                <span className="ml-auto font-mono text-lg font-bold text-slate-900">
                  {plan.price}
                </span>
              </div>

              {plan.priceNote ? (
                <p className="mt-1 text-xs text-slate-400">{plan.priceNote}</p>
              ) : null}

              <p className="mt-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Best for: {plan.bestFor}
              </p>

              <p className="mt-3 text-sm leading-relaxed text-slate-700">{plan.summary}</p>

              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-emerald-700">
                    What&apos;s included
                  </p>
                  <ul className="space-y-1.5 text-sm text-slate-700">
                    {plan.includes.map((item) => (
                      <li key={item} className="flex items-start gap-2">
                        <span className="mt-1 flex-shrink-0 text-emerald-500" aria-hidden="true">
                          ✓
                        </span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-amber-600">
                    Limitations / things to know
                  </p>
                  <ul className="space-y-1.5 text-sm text-slate-700">
                    {plan.limitations.map((item) => (
                      <li key={item} className="flex items-start gap-2">
                        <span className="mt-1 flex-shrink-0 text-amber-400" aria-hidden="true">
                          ·
                        </span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </article>
          ))}
        </section>

        {/* Use case recommendations */}
        <section className="mb-12">
          <h2 className="mb-4 text-2xl font-bold text-slate-950">
            Which plan for your use case?
          </h2>
          <div className="space-y-3">
            {USE_CASES.map((uc) => (
              <div
                key={uc.label}
                className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
              >
                <div className="flex flex-col gap-1 md:flex-row md:items-center md:gap-6">
                  <p className="font-semibold text-slate-950 md:w-64 md:flex-shrink-0">
                    {uc.label}
                  </p>
                  <p className="rounded-full bg-purple-100 px-3 py-0.5 text-xs font-bold text-purple-800 md:flex-shrink-0">
                    {uc.recommendedPlan}
                  </p>
                </div>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{uc.reasoning}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Value analysis */}
        <section className="mb-12 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-950">Is ElevenLabs worth paying for?</h2>
          <div className="mt-5 space-y-4 text-sm leading-7 text-slate-700">
            <p>
              The free plan gives you a meaningful sample of the platform — enough to verify
              voice quality and test a use case. If your use case is light or one-off, free or
              Starter may be all you ever need.
            </p>
            <p>
              The Creator plan at $22/month is where the platform starts to make economic sense
              for working creators. If you are producing regular content — weekly YouTube videos,
              podcast episodes, or client voiceovers — the cost is typically low relative to the
              time saved compared to traditional voiceover production or recording.
            </p>
            <p>
              The Pro plan at $99/month is only worth it if voice content is a consistent part
              of professional work. If you are billing clients for voice work, running a studio,
              or building an application, the higher limits and API access justify the cost. For
              individual hobbyists, it is unlikely to be worth it.
            </p>
            <p>
              Scale and Business tiers are narrowly targeted at organisations where voice
              generation volume is high and the cost-per-unit economics of producing content at
              scale outweigh traditional production costs.
            </p>
          </div>
        </section>

        {/* Limitations */}
        <section className="mb-12 rounded-3xl border border-amber-200 bg-amber-50/40 p-6">
          <h2 className="text-xl font-bold text-slate-950">
            Important considerations before paying
          </h2>
          <ul className="mt-4 space-y-3 text-sm text-slate-700">
            {[
              "ElevenLabs uses a voice generation limit model. Going over your monthly allowance requires upgrading or purchasing additional capacity. Monitor your usage carefully in your first month.",
              "Voice cloning — training the platform on your own voice — is available from Creator upward. Quality and the number of custom voices varies by plan; verify the current limits on the official pricing page.",
              "Pricing is in USD. If you are paying in another currency, account for conversion rates and potential bank fees.",
              "Annual billing typically costs less per month than monthly billing. If you commit, verify the annual discount on the official pricing page.",
              "ElevenLabs can change pricing, plan limits, and feature availability. What is documented here reflects research dated " + VERIFIED_DATE + ". Always verify before purchasing.",
              "Commercial rights are included from Starter upward. The Free plan does not grant commercial use rights.",
            ].map((item) => (
              <li key={item} className="flex items-start gap-3">
                <span className="mt-1 flex-shrink-0 text-amber-600" aria-hidden="true">
                  ⚠
                </span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* Alternatives section */}
        <section className="mb-12 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-950">ElevenLabs alternatives</h2>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">
            ElevenLabs is a leading AI voice platform, but it is not the only option. Other
            well-regarded voice AI tools include Murf AI (strong for presentations and corporate
            voiceover), Descript (integrated with video and podcast editing), and Runway (focused
            on video generation with voice support).
          </p>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">
            The right choice depends on your primary use case. If you are working primarily with
            video editing, a tool that integrates voice into a broader editing workflow may be more
            efficient than a standalone voice platform.
          </p>
          <p className="mt-4 text-xs text-slate-400">
            LeTrusto is preparing a full comparison guide covering ElevenLabs alternatives. In
            the meantime, you can browse the{" "}
            <Link
              href="/ai-tools"
              className="text-purple-700 underline underline-offset-2 hover:text-purple-900"
            >
              AI tools catalog
            </Link>{" "}
            to compare options.
          </p>
        </section>

        {/* Final recommendation */}
        <section className="mb-10 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-950">Final recommendation</h2>
          <div className="mt-4 space-y-3 text-sm leading-relaxed text-slate-700">
            <p>
              <strong className="text-slate-900">Start with the Free plan</strong> if you have
              not yet tested ElevenLabs voice quality for your use case. There is no obligation
              and no payment required.
            </p>
            <p>
              <strong className="text-slate-900">Upgrade to Creator ($22/month)</strong> when
              you have a confirmed content production workflow — weekly videos, regular podcast
              episodes, or recurring client work — and need commercial rights and voice cloning.
              This is where the platform provides clear value for most individual creators.
            </p>
            <p>
              <strong className="text-slate-900">Move to Pro ($99/month)</strong> only when your
              volume or professional needs consistently push against Creator's limits, or when you
              need priority support and higher API access.
            </p>
            <p>
              Do not skip straight to Pro or Scale based on aspirational plans. Start at Free or
              Creator, run one production cycle, and evaluate whether the limits are actually a
              constraint.
            </p>
          </div>
        </section>

        {/* Affiliate CTA — uses same pattern as ai-tools/[slug]/page.tsx */}
        <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-900">Try ElevenLabs</h2>
          <p className="mt-2 text-sm text-slate-600">
            ElevenLabs offers a free plan that requires no credit card. You can evaluate voice
            quality before committing to a paid tier.
          </p>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            {hasAffiliate && affiliateUrl ? (
              <a
                href={affiliateUrl}
                target="_blank"
                rel="noreferrer sponsored"
                className="rounded-xl bg-purple-600 px-5 py-3 text-sm font-bold text-white hover:bg-purple-700"
              >
                Explore ElevenLabs →
              </a>
            ) : (
              <a
                href={OFFICIAL_SITE_URL}
                target="_blank"
                rel="noreferrer"
                className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
              >
                Visit ElevenLabs website
              </a>
            )}
            <a
              href={OFFICIAL_PRICING_URL}
              target="_blank"
              rel="noreferrer"
              className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 hover:border-slate-500"
            >
              View official pricing
            </a>
          </div>
          {hasAffiliate ? (
            <p className="mt-4 text-xs text-slate-400">
              Affiliate link — LeTrusto may earn a commission when you sign up through this link at no extra cost to you.{" "}
              <Link
                href="/affiliate-disclosure"
                className="underline hover:text-slate-600"
              >
                Learn more
              </Link>
            </p>
          ) : null}
        </section>

        {/* Footer nav */}
        <div className="flex flex-wrap items-center gap-4 border-t border-slate-100 pt-8">
          <Link
            href="/guides"
            className="rounded-xl border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-700 hover:border-slate-500"
          >
            ← All guides
          </Link>
          <Link
            href="/ai-tools"
            className="rounded-xl border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-700 hover:border-slate-500"
          >
            Browse AI tools
          </Link>
          <Link
            href="/methodology"
            className="text-xs text-slate-400 underline underline-offset-2 hover:text-slate-600"
          >
            How we research
          </Link>
        </div>

        <p className="mt-6 text-xs text-slate-400">
          Last verified: {VERIFIED_DATE} · Pricing and plan features subject to change. Verify
          at{" "}
          <a
            href={OFFICIAL_PRICING_URL}
            target="_blank"
            rel="noreferrer"
            className="underline hover:text-slate-600"
          >
            elevenlabs.io/pricing
          </a>
        </p>
      </div>
    </main>
  );
}
