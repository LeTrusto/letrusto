import type { Metadata } from "next";
import Link from "next/link";

import SchemaOrg from "@/components/SchemaOrg";
import { getAiToolBySlug } from "@/services/ai-tools.service";

const VERIFIED_DATE = "2026-08-10";
const ELEVENLABS_SITE = "https://elevenlabs.io";
const ELEVENLABS_PRICING = "https://elevenlabs.io/pricing";
const MURF_SITE = "https://murf.ai";
const MURF_PRICING = "https://murf.ai/pricing";

export const metadata: Metadata = {
  title: "ElevenLabs vs Murf AI: Which AI Voice Tool Is Right for You?",
  description:
    "A data-driven comparison of ElevenLabs and Murf AI — pricing, voices, features, and use-case fit — to help you choose the right AI voice platform.",
  alternates: {
    canonical: "/guides/elevenlabs-vs-murf-ai",
  },
  openGraph: {
    title: "ElevenLabs vs Murf AI: Which AI Voice Tool Is Right for You?",
    description:
      "A data-driven comparison of ElevenLabs and Murf AI — pricing, voices, features, and use-case fit — to help you choose the right AI voice platform.",
    url: "/guides/elevenlabs-vs-murf-ai",
    siteName: "LeTrusto",
    type: "article",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "ElevenLabs vs Murf AI: Which AI Voice Tool Is Right for You?",
    description:
      "A data-driven comparison of ElevenLabs and Murf AI — pricing, voices, features, and use-case fit — to help you choose the right AI voice platform.",
    images: ["/images/og-default.svg"],
  },
};

// Pricing verified from elevenlabs.io/pricing (2026-08-10)
const EL_PLANS = [
  { name: "Free", monthly: "$0", annual: "$0", note: "No credit card required" },
  { name: "Starter", monthly: "$6", annual: "$5/mo equivalent", note: "Commercial license, Instant Voice Cloning" },
  { name: "Creator", monthly: "$22", annual: "$18.33/mo equivalent", note: "Professional Voice Cloning; first month $11 (promo — may change)", highlight: true },
  { name: "Pro", monthly: "$99", annual: "$82.50/mo equivalent", note: "44.1kHz PCM audio via API, 192kbps" },
  { name: "Scale", monthly: "$299", annual: "$249.17/mo equivalent", note: "3 workspace seats, 3 Professional Voice Clones" },
  { name: "Business", monthly: "$990", annual: "$825/mo equivalent", note: "10 seats, 10 Voice Clones, low-latency TTS" },
  { name: "Enterprise", monthly: "Custom", annual: "Custom", note: "Custom terms, HIPAA BAAs, custom SSO" },
];

// Pricing verified from murf.ai/pricing (2026-08-10)
const MURF_PLANS = [
  { name: "Free", monthly: "$0", annual: "$0", note: "10 min voice generation, 10 projects, no commercial rights" },
  { name: "Creator", monthly: "$19", annual: "$228/year", note: "24 hrs/Year voice generation, 100 projects, commercial rights" },
  { name: "Business", monthly: "$66", annual: "$792/year", note: "96 hrs/Year voice generation, 500 projects, business license, PowerPoint & Google Slides", highlight: true },
  { name: "Enterprise", monthly: "Custom", annual: "Custom", note: "Unlimited generation, SSO, AI Translation, custom voice clones (add-on)" },
];

// All comparison rows verified from official sources 2026-08-10
type CompRow = { feature: string; el: string; murf: string; winner: "elevenlabs" | "murf" | "comparable" | "depends" };

const COMPARISON_ROWS: CompRow[] = [
  { feature: "Entry paid price", el: "$6/month (Starter)", murf: "$19/month (Creator)", winner: "elevenlabs" },
  { feature: "Creator-tier price", el: "$22/month", murf: "$19/month", winner: "murf" },
  { feature: "Voice library", el: "Over 11,000 voices", murf: "200+ voices", winner: "elevenlabs" },
  { feature: "Languages", el: "70+ (Eleven v3 model)", murf: "30+", winner: "elevenlabs" },
  { feature: "Instant Voice Cloning", el: "Starter+ ($6/mo)", murf: "Verify at murf.ai/pricing", winner: "elevenlabs" },
  { feature: "Professional Voice Cloning", el: "Creator+ ($22/mo)", murf: "Enterprise add-on (custom)", winner: "elevenlabs" },
  { feature: "Commercial rights", el: "All paid plans (Starter+)", murf: "Creator+", winner: "comparable" },
  { feature: "Built-in video timeline editor", el: "No", murf: "Yes (Voice over Video)", winner: "murf" },
  { feature: "PowerPoint integration", el: "No", murf: "Business+ plan only", winner: "murf" },
  { feature: "Google Slides integration", el: "No", murf: "Business+ plan only", winner: "murf" },
  { feature: "Canva integration", el: "Not listed on pricing page", murf: "Creator+ (listed)", winner: "murf" },
  { feature: "API access", el: "Yes (all plans)", murf: "Yes (Murf API available)", winner: "comparable" },
  { feature: "Mobile app", el: "iOS + Android", murf: "Not featured on pricing page", winner: "elevenlabs" },
  { feature: "Low-latency / real-time", el: "Flash v2.5 ~75ms inference", murf: "Not prominently stated", winner: "elevenlabs" },
  { feature: "Conversational AI focus", el: "Strong — ElevenAgents platform", murf: "Not a primary focus", winner: "elevenlabs" },
  { feature: "SOC 2 Type II", el: "Yes", murf: "Yes", winner: "comparable" },
  { feature: "ISO 27001", el: "Yes", murf: "Yes", winner: "comparable" },
  { feature: "GDPR", el: "Yes", murf: "Yes", winner: "comparable" },
  { feature: "HIPAA", el: "Eligible (enterprise workflows)", murf: "Compliant", winner: "comparable" },
];

const WINNER_LABEL: Record<CompRow["winner"], { label: string; cls: string }> = {
  elevenlabs: { label: "ElevenLabs", cls: "text-purple-700" },
  murf: { label: "Murf", cls: "text-blue-700" },
  comparable: { label: "Comparable", cls: "text-slate-500" },
  depends: { label: "Depends", cls: "text-amber-600" },
};

export default async function ElevenLabsVsMurfPage() {
  // Affiliate URL sourced from backend — never hardcoded in page.
  const tool = await getAiToolBySlug("elevenlabs");
  const hasAffiliate = Boolean(tool?.affiliateAvailable && tool?.affiliateUrl);
  const affiliateUrl = tool?.affiliateUrl ?? null;

  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)] px-6 pb-16 pt-10">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "ElevenLabs vs Murf AI: Which AI Voice Tool Is Right for You?",
          url: "https://letrusto.com/guides/elevenlabs-vs-murf-ai",
          description:
            "A data-driven comparison of ElevenLabs and Murf AI — pricing, voices, features, and use-case fit — to help you choose the right AI voice platform.",
        }}
      />

      <div className="mx-auto max-w-4xl">
        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="mb-6 text-xs text-slate-500">
          <ol className="flex flex-wrap items-center gap-1">
            <li><Link href="/" className="hover:text-slate-700">Home</Link></li>
            <li aria-hidden="true" className="text-slate-300">/</li>
            <li><Link href="/guides" className="hover:text-slate-700">Guides</Link></li>
            <li aria-hidden="true" className="text-slate-300">/</li>
            <li className="font-medium text-slate-700" aria-current="page">ElevenLabs vs Murf AI</li>
          </ol>
        </nav>

        {/* Header */}
        <header className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-purple-600">
            Comparison · AI Voice Tools
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
            ElevenLabs vs Murf AI: Which AI Voice Tool Is Right for You?
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-relaxed text-slate-600">
            Both ElevenLabs and Murf AI are capable AI voice platforms, but they serve
            different workflows. This guide compares them on pricing, voice quality, features,
            and use-case fit so you can choose confidently.
          </p>

          {/* Badge row */}
          <div className="mt-5 flex flex-wrap items-center gap-4 text-xs text-slate-400">
            <span>
              Last verified:{" "}
              <time dateTime={VERIFIED_DATE}>August 10, 2026</time>
            </span>
            <span>Category: AI Voice Generation</span>
            <Link href="/methodology" className="underline underline-offset-2 hover:text-slate-600">
              How we research
            </Link>
          </div>

          {/* Affiliate disclosure */}
          <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500">
            <strong className="font-semibold text-slate-700">Affiliate disclosure:</strong>{" "}
            LeTrusto is an approved affiliate partner of ElevenLabs. If you sign up through
            our ElevenLabs link, we may earn a commission at no extra cost to you. LeTrusto
            is not an affiliate partner of Murf AI — that link is a plain official website
            link. This does not influence our editorial assessment.{" "}
            <Link href="/affiliate-disclosure" className="font-medium text-purple-700 underline underline-offset-2 hover:text-purple-900">
              Learn more
            </Link>
          </div>
        </header>

        {/* Quick verdict */}
        <section className="mb-8 rounded-3xl border border-purple-200 bg-purple-50/50 p-6">
          <h2 className="text-xl font-bold text-slate-950">Quick verdict</h2>
          <ul className="mt-4 space-y-2.5 text-sm text-slate-700">
            <li className="flex gap-3">
              <span className="mt-1 flex-shrink-0 text-purple-600">→</span>
              <span>
                <strong>ElevenLabs is the stronger overall platform</strong> for individual
                content creators, developers, and multilingual voice production — with a larger
                voice library (over 11,000 voices), more languages (70+), lower entry pricing
                ($6/month), and purpose-built developer and conversational AI tools.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="mt-1 flex-shrink-0 text-purple-600">→</span>
              <span>
                <strong>Murf AI is the stronger choice for presentation-first workflows</strong>{" "}
                — it has a native video timeline editor and official integrations for PowerPoint
                and Google Slides that ElevenLabs does not offer.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="mt-1 flex-shrink-0 text-purple-600">→</span>
              <span>
                <strong>The decision depends on your primary workflow</strong>, not simply price.
                If you narrate slides and training videos, Murf's integrations may save you
                significant time. If you produce podcasts, YouTube videos, or build voice
                applications, ElevenLabs is the clearer choice.
              </span>
            </li>
          </ul>
        </section>

        {/* Pricing caveat */}
        <div className="mb-8 rounded-xl border border-amber-200 bg-amber-50/50 px-4 py-3 text-xs text-slate-600">
          <strong className="font-semibold text-slate-800">Pricing note:</strong>{" "}
          All pricing reflects official sources verified on August 10, 2026. Both ElevenLabs
          and Murf AI update their plans and pricing regularly. Always verify current prices
          before purchasing at{" "}
          <a href={ELEVENLABS_PRICING} target="_blank" rel="noreferrer" className="font-medium text-amber-800 underline underline-offset-2 hover:text-amber-900">
            elevenlabs.io/pricing
          </a>{" "}
          and{" "}
          <a href={MURF_PRICING} target="_blank" rel="noreferrer" className="font-medium text-amber-800 underline underline-offset-2 hover:text-amber-900">
            murf.ai/pricing
          </a>.
        </div>

        {/* At-a-glance comparison table */}
        <section className="mb-12">
          <h2 className="mb-4 text-2xl font-bold text-slate-950">At a glance</h2>

          <div className="grid gap-4 md:grid-cols-2">
            {/* ElevenLabs column */}
            <div className="rounded-2xl border border-purple-200 bg-white p-5 shadow-sm">
              <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-purple-600">ElevenLabs</p>
              <ul className="space-y-2 text-sm text-slate-700">
                <li><strong className="text-slate-900">Entry paid:</strong> $6/month (Starter)</li>
                <li><strong className="text-slate-900">Creator tier:</strong> $22/month</li>
                <li><strong className="text-slate-900">Voices:</strong> Over 11,000</li>
                <li><strong className="text-slate-900">Languages:</strong> 70+ (Eleven v3)</li>
                <li><strong className="text-slate-900">Voice cloning:</strong> Instant (Starter+), Professional (Creator+)</li>
                <li><strong className="text-slate-900">API:</strong> All plans</li>
                <li><strong className="text-slate-900">Mobile:</strong> iOS + Android</li>
                <li><strong className="text-slate-900">Low-latency model:</strong> Flash v2.5 ~75ms inference</li>
                <li><strong className="text-slate-900">Security:</strong> SOC 2 II, ISO 27001, GDPR, HIPAA-eligible</li>
              </ul>
            </div>

            {/* Murf column */}
            <div className="rounded-2xl border border-blue-200 bg-white p-5 shadow-sm">
              <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-blue-600">Murf AI</p>
              <ul className="space-y-2 text-sm text-slate-700">
                <li><strong className="text-slate-900">Entry paid:</strong> $19/month (Creator)</li>
                <li><strong className="text-slate-900">Business tier:</strong> $66/month</li>
                <li><strong className="text-slate-900">Voices:</strong> 200+</li>
                <li><strong className="text-slate-900">Languages:</strong> 30+</li>
                <li><strong className="text-slate-900">Voice generation:</strong> Creator 24 hrs/Year · Business 96 hrs/Year</li>
                <li><strong className="text-slate-900">PowerPoint integration:</strong> Business+</li>
                <li><strong className="text-slate-900">Google Slides:</strong> Business+</li>
                <li><strong className="text-slate-900">Canva:</strong> Creator+</li>
                <li><strong className="text-slate-900">Security:</strong> SOC 2 II, ISO 27001, GDPR, HIPAA</li>
              </ul>
            </div>
          </div>
        </section>

        {/* ElevenLabs overview */}
        <section className="mb-10 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-950">ElevenLabs overview</h2>
          <p className="mt-4 text-sm leading-relaxed text-slate-700">
            ElevenLabs is an AI voice platform built around high-quality speech generation,
            voice cloning, and developer-grade API access. It is widely used for content
            creation, audiobook production, podcasting, YouTube voiceovers, and building
            conversational AI applications.
          </p>

          <h3 className="mt-6 text-base font-bold text-slate-900">Pricing (monthly billing)</h3>
          <div className="mt-3 overflow-x-auto rounded-xl border border-slate-100">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left">
                  <th className="px-4 py-2.5 font-semibold text-slate-900">Plan</th>
                  <th className="px-4 py-2.5 font-semibold text-slate-900">Monthly</th>
                  <th className="px-4 py-2.5 font-semibold text-slate-900">Annual equiv.</th>
                  <th className="px-4 py-2.5 font-semibold text-slate-900">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {EL_PLANS.map((p) => (
                  <tr key={p.name} className={p.highlight ? "bg-purple-50/40" : ""}>
                    <td className={`px-4 py-2.5 font-medium ${p.highlight ? "text-purple-900" : "text-slate-900"}`}>
                      {p.name}
                      {p.highlight ? <span className="ml-2 rounded-full bg-purple-100 px-2 py-0.5 text-xs font-semibold text-purple-700">Popular</span> : null}
                    </td>
                    <td className="px-4 py-2.5 text-slate-700">{p.monthly}</td>
                    <td className="px-4 py-2.5 text-slate-700">{p.annual}</td>
                    <td className="px-4 py-2.5 text-slate-500">{p.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Annual plans = 10 months price (2 months free). Source: elevenlabs.io/pricing, 2026-08-10.
          </p>

          <h3 className="mt-6 text-base font-bold text-slate-900">Credits and how they work</h3>
          <p className="mt-2 text-sm leading-relaxed text-slate-700">
            ElevenLabs uses a credit system. Credits are shared across all products on the
            platform — Text to Speech, Speech to Text, Sound Effects, Voice Changer, Music,
            and Dubbing. The number of credits consumed depends on the product and the AI
            model used. For standard Text to Speech, approximately 1 credit is used per
            character of text. Unused credits roll over for up to 2 months (not on the Free
            plan).
          </p>
          <p className="mt-2 text-sm leading-relaxed text-slate-700">
            This means the credit counts shown above represent a shared pool across
            everything you use on ElevenLabs — not exclusively TTS minutes.
          </p>

          <h3 className="mt-6 text-base font-bold text-slate-900">Voice library and languages</h3>
          <div className="mt-2 text-sm leading-relaxed text-slate-700 space-y-2">
            <p>
              ElevenLabs provides access to over 11,000 voices in its Voice Library, spanning
              different ages, accents, tones, and styles. It also supports Voice Design (generate
              a new voice from a text prompt) and Voice Cloning (Instant from ~1 minute of audio
              on Starter+; Professional from 30+ minutes of audio on Creator+).
            </p>
            <p>
              Language support depends on the model: 70+ languages on Eleven v3, 29 languages
              on Multilingual v2, and 32 languages on Flash v2.5 and Turbo v2.5.
            </p>
          </div>

          <h3 className="mt-6 text-base font-bold text-slate-900">AI models</h3>
          <ul className="mt-2 space-y-1.5 text-sm text-slate-700">
            <li><strong className="text-slate-900">Eleven v3:</strong> Most expressive — supports audio tags ([whispers], [laughs], [excited]) — 70+ languages</li>
            <li><strong className="text-slate-900">Multilingual v2:</strong> Stable, lifelike output for long-form narration — 29 languages</li>
            <li><strong className="text-slate-900">Flash v2.5:</strong> Ultra-low latency (~75ms inference) — 32 languages — ideal for agents and real-time apps</li>
            <li><strong className="text-slate-900">Turbo v2.5:</strong> Balance of quality and speed — 32 languages</li>
          </ul>

          <h3 className="mt-6 text-base font-bold text-slate-900">Key use cases</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {["Podcasts", "YouTube voiceovers", "Audiobooks", "Conversational AI agents", "Gaming NPCs", "Accessibility", "Developer APIs", "Language learning", "Video narration"].map((uc) => (
              <span key={uc} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">{uc}</span>
            ))}
          </div>
        </section>

        {/* Murf AI overview */}
        <section className="mb-10 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-950">Murf AI overview</h2>
          <p className="mt-4 text-sm leading-relaxed text-slate-700">
            Murf AI is an AI voice platform with a built-in studio designed for voiceover
            production. Its standout feature set — video timeline editor, PowerPoint plugin,
            Google Slides integration — makes it a practical choice for eLearning, corporate
            training, and presentation-focused content workflows.
          </p>

          <h3 className="mt-6 text-base font-bold text-slate-900">Pricing (monthly billing)</h3>
          <div className="mt-3 overflow-x-auto rounded-xl border border-slate-100">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left">
                  <th className="px-4 py-2.5 font-semibold text-slate-900">Plan</th>
                  <th className="px-4 py-2.5 font-semibold text-slate-900">Monthly</th>
                  <th className="px-4 py-2.5 font-semibold text-slate-900">Annual</th>
                  <th className="px-4 py-2.5 font-semibold text-slate-900">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {MURF_PLANS.map((p) => (
                  <tr key={p.name} className={p.highlight ? "bg-blue-50/30" : ""}>
                    <td className={`px-4 py-2.5 font-medium ${p.highlight ? "text-blue-900" : "text-slate-900"}`}>
                      {p.name}
                      {p.highlight ? <span className="ml-2 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700">Best value</span> : null}
                    </td>
                    <td className="px-4 py-2.5 text-slate-700">{p.monthly}</td>
                    <td className="px-4 py-2.5 text-slate-700">{p.annual}</td>
                    <td className="px-4 py-2.5 text-slate-500">{p.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Source: murf.ai/pricing, 2026-08-10. Voice generation time is shown using the official
            &ldquo;hrs/Year&rdquo; wording from the Murf pricing page.
          </p>

          <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50/40 px-4 py-3 text-xs text-slate-600">
            <strong className="font-semibold">Note on &ldquo;hrs/Year&rdquo;:</strong>{" "}
            Murf&apos;s pricing page states voice generation as &ldquo;24 hrs/Year&rdquo; (Creator)
            and &ldquo;96 hrs/Year&rdquo; (Business). This is the official wording. Before purchasing,
            verify exactly how this limit applies — annually, monthly, or another cadence —
            directly at{" "}
            <a href={MURF_PRICING} target="_blank" rel="noreferrer" className="underline hover:text-amber-800">
              murf.ai/pricing
            </a>.
          </div>

          <h3 className="mt-6 text-base font-bold text-slate-900">Voice library and languages</h3>
          <p className="mt-2 text-sm leading-relaxed text-slate-700">
            Murf provides 200+ AI voices across 30+ languages and accents. Voice styles and
            tonalities are unlimited across paid plans. Commercial rights are included from
            the Creator plan; a Business License (broader usage rights) requires the Business plan.
          </p>

          <h3 className="mt-6 text-base font-bold text-slate-900">Integrations and workflow features</h3>
          <ul className="mt-2 space-y-1.5 text-sm text-slate-700">
            <li><strong className="text-slate-900">Canva add-on:</strong> Available from Creator plan</li>
            <li><strong className="text-slate-900">PowerPoint plugin:</strong> Business plan and above</li>
            <li><strong className="text-slate-900">Google Slides:</strong> Business plan and above</li>
            <li><strong className="text-slate-900">Voice over Video:</strong> Sync voiceover with video timeline in-studio</li>
            <li><strong className="text-slate-900">Murf Voices for Windows apps:</strong> Business plan</li>
            <li><strong className="text-slate-900">Audio to Text:</strong> Business plan</li>
          </ul>

          <h3 className="mt-6 text-base font-bold text-slate-900">Key use cases</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {["eLearning", "Corporate training", "PowerPoint narration", "Google Slides voiceover", "Explainer videos", "Product demos", "Presentations", "IVR voices", "Advertising"].map((uc) => (
              <span key={uc} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">{uc}</span>
            ))}
          </div>
        </section>

        {/* Feature-by-feature comparison */}
        <section className="mb-12">
          <h2 className="mb-4 text-2xl font-bold text-slate-950">Feature comparison</h2>
          <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left">
                  <th className="px-5 py-3 font-bold text-slate-900">Feature</th>
                  <th className="px-5 py-3 font-bold text-purple-800">ElevenLabs</th>
                  <th className="px-5 py-3 font-bold text-blue-800">Murf AI</th>
                  <th className="px-5 py-3 font-bold text-slate-500">Advantage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {COMPARISON_ROWS.map((row) => {
                  const w = WINNER_LABEL[row.winner];
                  return (
                    <tr key={row.feature} className="hover:bg-slate-50/50">
                      <td className="px-5 py-3 font-medium text-slate-900">{row.feature}</td>
                      <td className="px-5 py-3 text-slate-700">{row.el}</td>
                      <td className="px-5 py-3 text-slate-700">{row.murf}</td>
                      <td className={`px-5 py-3 text-xs font-semibold ${w.cls}`}>{w.label}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-slate-400">
            All data from official provider sources, August 10, 2026. Verify before purchasing.
          </p>
        </section>

        {/* Who should choose ElevenLabs */}
        <section className="mb-8 rounded-3xl border border-purple-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-950">Who should choose ElevenLabs?</h2>
          <p className="mt-3 text-sm text-slate-600">
            ElevenLabs is the stronger option when:
          </p>
          <ul className="mt-4 space-y-2.5 text-sm text-slate-700">
            {[
              "You create regular YouTube content and need commercial-licensed voiceover at the lowest entry price ($6/month Starter).",
              "You produce podcasts and need high-quality, consistent narration with the option to clone your own voice (Creator, $22/month).",
              "You create audiobooks or long-form narrated content and need emotionally expressive voice output.",
              "You are a developer building voice into an application and need API access, low-latency generation (Flash v2.5 ~75ms), or conversational AI features.",
              "You need voice content in more than 30 languages — ElevenLabs supports 70+ on its Eleven v3 model.",
              "You want access to the largest AI voice library — over 11,000 voices across accents, tones, and styles.",
              "You want Professional Voice Cloning from the Creator tier ($22/month) without an enterprise contract.",
              "You need a mobile app for on-the-go audio generation.",
            ].map((item) => (
              <li key={item} className="flex items-start gap-2">
                <span className="mt-1 flex-shrink-0 text-purple-500" aria-hidden="true">✓</span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* Who should choose Murf */}
        <section className="mb-12 rounded-3xl border border-blue-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-950">Who should choose Murf AI?</h2>
          <p className="mt-3 text-sm text-slate-600">
            Murf AI is the stronger option when:
          </p>
          <ul className="mt-4 space-y-2.5 text-sm text-slate-700">
            {[
              "Your core workflow involves narrating PowerPoint presentations — Murf has an official PowerPoint plugin (Business plan) that ElevenLabs does not offer.",
              "You create Google Slides-based training or educational content and want built-in voiceover integration (Business plan).",
              "You produce eLearning modules and need a studio that syncs audio directly to a video timeline without additional editing software.",
              "Your team uses Canva for design work and wants Murf AI voices accessible within that tool (Creator plan).",
              "You work in corporate L&D and need enterprise HIPAA compliance, a business license, and a tool that non-technical team members can use independently.",
              "Your content production is primarily presentation-based rather than API-driven or developer-centric.",
            ].map((item) => (
              <li key={item} className="flex items-start gap-2">
                <span className="mt-1 flex-shrink-0 text-blue-500" aria-hidden="true">✓</span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* Detailed pricing comparison */}
        <section className="mb-10 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-950">Pricing in depth</h2>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">
            Both tools have free plans for evaluation and paid plans that unlock commercial
            rights. The biggest structural difference is that ElevenLabs starts at $6/month
            (Starter) for the first paid tier, while Murf starts at $19/month (Creator).
          </p>

          <div className="mt-6 grid gap-6 md:grid-cols-2">
            <div>
              <h3 className="mb-3 text-sm font-bold uppercase tracking-widest text-purple-700">ElevenLabs</h3>
              <ul className="space-y-2 text-sm text-slate-700">
                <li><span className="font-semibold">Free:</span> $0 · ~10 min TTS/month · No commercial rights</li>
                <li><span className="font-semibold">Starter:</span> $6/mo ($5/mo annually) · Commercial + Instant Cloning</li>
                <li><span className="font-semibold">Creator:</span> $22/mo ($18.33/mo annually) · Professional Voice Cloning</li>
                <li><span className="font-semibold">Pro:</span> $99/mo ($82.50/mo annually) · 192kbps audio · PCM via API</li>
                <li><span className="font-semibold">Scale:</span> $299/mo ($249.17/mo annually) · 3 seats</li>
                <li><span className="font-semibold">Business:</span> $990/mo ($825/mo annually) · 10 seats</li>
                <li><span className="font-semibold">Enterprise:</span> Custom</li>
              </ul>
              <p className="mt-3 text-xs text-slate-400">Annual = 10 months price. Creator first month: $11 (promotional — verify at elevenlabs.io/pricing).</p>
            </div>
            <div>
              <h3 className="mb-3 text-sm font-bold uppercase tracking-widest text-blue-700">Murf AI</h3>
              <ul className="space-y-2 text-sm text-slate-700">
                <li><span className="font-semibold">Free:</span> $0 · 10 min generation · No commercial rights</li>
                <li><span className="font-semibold">Creator:</span> $19/mo · $228/year · 24 hrs/Year voice generation</li>
                <li><span className="font-semibold">Business:</span> $66/mo · $792/year · 96 hrs/Year voice generation</li>
                <li><span className="font-semibold">Enterprise:</span> Custom · Unlimited generation</li>
              </ul>
              <p className="mt-3 text-xs text-slate-400">
                Annual totals sourced from murf.ai/pricing, August 2026.
                Monthly-equivalent calculations: Creator ≈ $19/mo ($228÷12); Business ≈ $66/mo ($792÷12).
                These figures are simple arithmetic from the confirmed annual totals.
              </p>
            </div>
          </div>
        </section>

        {/* Important limitations */}
        <section className="mb-10 rounded-3xl border border-amber-200 bg-amber-50/40 p-6">
          <h2 className="text-xl font-bold text-slate-950">Important limitations before you decide</h2>
          <ul className="mt-4 space-y-3 text-sm text-slate-700">
            {[
              "Pricing changes frequently. The figures above reflect August 2026. Always verify the current price at elevenlabs.io/pricing and murf.ai/pricing before purchasing.",
              "ElevenLabs credits are shared across all products — Text to Speech, Speech to Text, Sound Effects, Voice Changer, Music, Dubbing. Credits are not exclusively TTS minutes. If you use credits on other products, TTS capacity decreases.",
              "The ElevenLabs Creator plan shows $11 for the first month on the pricing page (50% promotional discount). The standard ongoing price is $22/month. This promotion may change.",
              "Murf AI's pricing page states voice generation as \"24 hrs/Year\" (Creator) and \"96 hrs/Year\" (Business). We have not reinterpreted this figure. Verify what this means in practice directly with Murf before purchasing.",
              "Murf AI voice cloning availability on Creator and Business plans is not clearly documented on the pricing page. Custom voice clones appear only as an Enterprise add-on. Verify this with Murf before purchasing if voice cloning is important to you.",
              "LeTrusto is not yet an affiliate partner of Murf AI. The Murf AI link in this guide is a plain official website link that earns LeTrusto no commission.",
              "LeTrusto has not independently tested either platform. This guide is based on publicly documented product information only.",
            ].map((item) => (
              <li key={item} className="flex items-start gap-3">
                <span className="mt-1 flex-shrink-0 text-amber-600" aria-hidden="true">⚠</span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* Our recommendation */}
        <section className="mb-10 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-950">Our recommendation</h2>
          <div className="mt-5 space-y-4 text-sm leading-7 text-slate-700">
            <p>
              <strong className="text-slate-900">For most individual content creators, ElevenLabs is the stronger starting point.</strong> The Starter plan at $6/month is the lowest paid entry point in the AI voice market with genuine commercial rights. The Creator plan at $22/month adds Professional Voice Cloning — a feature that typically requires enterprise contracts elsewhere. The voice library (over 11,000 voices, 70+ languages) is substantially larger than Murf&apos;s 200+ voices.
            </p>
            <p>
              <strong className="text-slate-900">For eLearning designers and corporate L&D teams, Murf AI is worth serious evaluation.</strong> The PowerPoint plugin, Google Slides integration, and video timeline editor are features that directly address the presentation-narration workflow — something ElevenLabs does not currently offer in the same integrated way.
            </p>
            <p>
              <strong className="text-slate-900">The decision should be driven by your primary workflow, not price alone.</strong> At the creator tier the price difference is only $3/month ($22 vs $19). The voice library, language support, and integration ecosystem are more likely to determine long-term fit than the monthly cost delta.
            </p>
            <p>
              Both platforms offer a free plan. Start with the free tier of whichever tool aligns with your workflow — evaluate voice quality for your specific use case — then upgrade only when you have a concrete production need.
            </p>
          </div>
        </section>

        {/* CTA section */}
        <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-900">Try both platforms</h2>
          <p className="mt-2 text-sm text-slate-600">
            Both ElevenLabs and Murf AI offer free plans. You can evaluate voice quality with
            no credit card required.
          </p>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {/* ElevenLabs CTA — affiliate if backend configured */}
            <div className="rounded-2xl border border-purple-200 bg-purple-50/30 p-4">
              <p className="mb-3 text-sm font-bold text-purple-900">ElevenLabs</p>
              <p className="mb-4 text-xs leading-relaxed text-slate-600">
                Over 11,000 voices · 70+ languages · Starts at $6/month
              </p>
              <div className="flex flex-col gap-2">
                {hasAffiliate && affiliateUrl ? (
                  <a
                    href={affiliateUrl}
                    target="_blank"
                    rel="noreferrer sponsored"
                    className="rounded-xl bg-purple-600 px-5 py-2.5 text-center text-sm font-bold text-white hover:bg-purple-700"
                  >
                    Explore ElevenLabs →
                  </a>
                ) : (
                  <a
                    href={ELEVENLABS_SITE}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-xl bg-slate-900 px-5 py-2.5 text-center text-sm font-semibold text-white hover:bg-slate-800"
                  >
                    Visit ElevenLabs
                  </a>
                )}
                <a
                  href={ELEVENLABS_PRICING}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-xl border border-purple-300 px-5 py-2.5 text-center text-xs font-medium text-purple-700 hover:border-purple-500"
                >
                  View pricing
                </a>
              </div>
              {hasAffiliate ? (
                <p className="mt-3 text-xs text-slate-400">
                  Affiliate link — LeTrusto earns a commission if you sign up through this link at no extra cost to you.{" "}
                  <Link href="/affiliate-disclosure" className="underline hover:text-slate-600">Learn more</Link>
                </p>
              ) : null}
            </div>

            {/* Murf CTA — official link only, no affiliate */}
            <div className="rounded-2xl border border-slate-200 bg-slate-50/30 p-4">
              <p className="mb-3 text-sm font-bold text-slate-900">Murf AI</p>
              <p className="mb-4 text-xs leading-relaxed text-slate-600">
                200+ voices · 30+ languages · Starts at $19/month (Creator)
              </p>
              <div className="flex flex-col gap-2">
                <a
                  href={MURF_SITE}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-center text-sm font-semibold text-slate-700 hover:border-slate-500"
                >
                  Visit Murf AI
                </a>
                <a
                  href={MURF_PRICING}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-xl border border-slate-200 px-5 py-2.5 text-center text-xs font-medium text-slate-500 hover:border-slate-400"
                >
                  View pricing
                </a>
              </div>
              <p className="mt-3 text-xs text-slate-400">
                Official website link — not an affiliate link. LeTrusto earns no commission from Murf AI.
              </p>
            </div>
          </div>
        </section>

        {/* Footer nav */}
        <div className="flex flex-wrap items-center gap-4 border-t border-slate-100 pt-8">
          <Link href="/guides" className="rounded-xl border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-700 hover:border-slate-500">
            ← All guides
          </Link>
          <Link href="/ai-tools" className="rounded-xl border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-700 hover:border-slate-500">
            Browse AI tools
          </Link>
          <Link href="/methodology" className="text-xs text-slate-400 underline underline-offset-2 hover:text-slate-600">
            How we research
          </Link>
        </div>

        <p className="mt-6 text-xs text-slate-400">
          Last verified: August 10, 2026 · Always verify current pricing at{" "}
          <a href={ELEVENLABS_PRICING} target="_blank" rel="noreferrer" className="underline hover:text-slate-600">elevenlabs.io/pricing</a>
          {" "}and{" "}
          <a href={MURF_PRICING} target="_blank" rel="noreferrer" className="underline hover:text-slate-600">murf.ai/pricing</a>
        </p>
      </div>
    </main>
  );
}
