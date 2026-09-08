import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRight,
  Check,
  Code2,
  Eye,
  Gauge,
  HeartHandshake,
  ShieldCheck,
  Sparkles,
  Users,
  Zap,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

import SchemaOrg from "@/components/SchemaOrg";
import LiveProofPreview from "@/components/saas/LiveProofPreview";

export const metadata: Metadata = {
  title: "About LeTrusto",
  description: "Learn how LeTrusto helps growing businesses turn customer confidence into visible momentum.",
  alternates: {
    canonical: "/about",
  },
  openGraph: {
    title: "About LeTrusto",
    description: "Learn how LeTrusto helps growing businesses turn customer confidence into visible momentum.",
    url: "/about",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "About LeTrusto",
    description: "Learn how LeTrusto helps growing businesses turn customer confidence into visible momentum.",
    images: ["/images/og-default.svg"],
  },
};

export default function AboutPage() {
  return (
    <main className="overflow-hidden bg-[var(--background)] text-[var(--text-primary)]">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "About LeTrusto",
          url: "https://letrusto.com/about",
          description: "Learn how LeTrusto helps growing businesses turn customer confidence into visible momentum.",
        }}
      />
      <section className="relative border-b border-[#d9e5df] bg-[#17382e] text-[#f7faf8]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_84%_18%,rgba(37,99,235,0.32),transparent_28%),radial-gradient(circle_at_10%_80%,rgba(20,184,166,0.2),transparent_30%)]" />
        <div className="relative mx-auto grid max-w-7xl items-center gap-12 px-5 py-16 sm:px-8 sm:py-24 lg:grid-cols-[1.08fr_0.92fr] lg:gap-20 lg:px-12">
          <div>
            <p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.24em] text-[#60a5fa]"><Sparkles className="h-3.5 w-3.5" /> About LeTrusto</p>
            <h1 className="mt-5 max-w-3xl text-5xl font-black leading-[0.98] tracking-[-0.04em] sm:text-7xl">Make trust easier to <span className="text-[#60a5fa]">see.</span></h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-[#c5d7cf] sm:text-lg">LeTrusto helps growing businesses turn real customer activity into clear, timely social proof that gives the next visitor a reason to move.</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/register" className="lt-btn lt-btn-md bg-[#2563eb] text-white hover:bg-blue-500">Start building <ArrowRight className="h-4 w-4" /></Link>
              <Link href="/how-it-works" className="lt-btn lt-btn-md border border-[#638378] text-white hover:border-[#60a5fa]">See how it works</Link>
            </div>
          </div>
          <div className="border border-[#638378] bg-[#22483c] p-3 shadow-[0_24px_70px_rgba(0,0,0,0.2)]"><LiveProofPreview color="#2563eb" compact /></div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-20 sm:px-8 lg:px-12 lg:py-28">
        <div className="grid gap-12 lg:grid-cols-[0.85fr_1.15fr] lg:items-start">
          <div><p className="lt-label text-[#2563eb]">Our mission</p><h2 className="lt-heading-2 mt-3 max-w-md">Confidence should be part of the experience.</h2></div>
          <div className="space-y-5 text-base leading-7 text-[var(--text-secondary)]"><p>People make better decisions when they can see evidence from people like them. Businesses deserve a simple way to make that evidence useful without interrupting the experience they have worked hard to create.</p><p>We are building the trust layer for modern customer journeys: lightweight enough to install quickly, thoughtful enough to feel native, and transparent enough for teams to stay in control.</p></div>
        </div>
        <div className="mt-16 grid gap-5 md:grid-cols-3">
          <ValueCard icon={Users} title="Human signals" text="Bring real activity, reviews, and customer stories into the moments where they matter." />
          <ValueCard icon={Gauge} title="Useful by default" text="Keep the setup focused, the controls practical, and the signal easy to understand." />
          <ValueCard icon={Eye} title="Visible impact" text="Give teams a clear view of what is being shown and how their audience responds." />
        </div>
      </section>

      <section className="border-y border-[#d9e5df] bg-[#edf5f1] px-5 py-20 sm:px-8 lg:px-12 lg:py-28">
        <div className="mx-auto max-w-7xl"><div className="max-w-2xl"><p className="lt-label text-[#2563eb]">The product</p><h2 className="lt-heading-2 mt-3">A calm, capable home for customer proof.</h2><p className="lt-body mt-5">LeTrusto brings the collection, curation, and display of social proof into one workspace, so your team can spend less time stitching tools together and more time serving customers.</p></div>
          <div className="mt-12 grid gap-4 lg:grid-cols-3"><ProductCard icon={Zap} title="Live activity" text="Show recent signups, bookings, and purchases as a quiet rhythm of momentum." /><ProductCard icon={HeartHandshake} title="Customer stories" text="Collect and curate the words that sound like your future customers." /><ProductCard icon={Code2} title="Lightweight embeds" text="Install a focused widget with one script and control its behavior from your workspace." /></div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-20 sm:px-8 lg:px-12 lg:py-28"><div className="grid gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:items-center"><div><p className="lt-label text-[#2563eb]">How it works</p><h2 className="lt-heading-2 mt-3 max-w-lg">From customer moment to meaningful signal.</h2><div className="mt-8 space-y-6">{[["01", "Connect your events", "Choose the customer moments that tell the clearest story for your business."], ["02", "Curate the experience", "Set the tone, placement, and visibility rules so proof feels like part of your product."], ["03", "Learn and improve", "Watch the signal work, then refine what you show as your customer story grows."]].map(([number, title, text]) => <div key={number} className="flex gap-4"><span className="flex h-9 w-9 shrink-0 items-center justify-center bg-[#2563eb] text-xs font-black text-white">{number}</span><div><h3 className="lt-heading-3">{title}</h3><p className="lt-body-sm mt-1">{text}</p></div></div>)}</div></div><div className="border border-[var(--border)] bg-[var(--surface)] p-3 shadow-[var(--shadow-lg)]"><LiveProofPreview color="#e11d48" /></div></div></section>

      <section className="border-y border-[#d9e5df] bg-[#f7faf8] px-5 py-20 sm:px-8 lg:px-12 lg:py-28"><div className="mx-auto max-w-7xl"><div className="max-w-2xl"><p className="lt-label text-[#2563eb]">Our trust principles</p><h2 className="lt-heading-2 mt-3">The standard behind every signal.</h2></div><div className="mt-12 grid gap-4 md:grid-cols-2"><Principle icon={ShieldCheck} title="Evidence over theatre" text="We favor useful, recognizable customer signals over noise, inflated claims, or attention for its own sake." /><Principle icon={HeartHandshake} title="Respect the customer" text="The customer experience comes first. Proof should help people decide, never pressure them into a decision." /><Principle icon={Check} title="Control stays with you" text="Your team chooses what is approved, what is visible, and how the experience fits your brand." /><Principle icon={Sparkles} title="Keep improving" text="The best trust experience is never finished. We build for learning, iteration, and steady progress." /></div></div></section>

      <section className="mx-auto max-w-7xl px-5 py-20 sm:px-8 lg:px-12 lg:py-28"><div className="border border-[#17382e] bg-[#17382e] p-8 text-center text-white sm:p-14"><p className="text-[10px] font-bold uppercase tracking-[0.24em] text-[#60a5fa]">Build trust into the next step</p><h2 className="mx-auto mt-4 max-w-2xl text-3xl font-black tracking-tight sm:text-5xl">Your next customer is already looking for a reason to believe.</h2><p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-[#c5d7cf]">Give them a clear signal with a LeTrusto widget built around the way your business earns confidence.</p><Link href="/register" className="lt-btn lt-btn-md mt-8 bg-[#2563eb] text-white hover:bg-blue-500">Create your free workspace <ArrowRight className="h-4 w-4" /></Link></div></section>
    </main>
  );
}

function ValueCard({ icon: Icon, title, text }: { icon: LucideIcon; title: string; text: string }) {
  return <article className="lt-card lt-card-hover"><div className="flex h-11 w-11 items-center justify-center bg-[#17382e] text-white"><Icon className="h-5 w-5" /></div><h3 className="lt-heading-3 mt-7">{title}</h3><p className="lt-body-sm mt-3">{text}</p></article>;
}

function ProductCard({ icon: Icon, title, text }: { icon: LucideIcon; title: string; text: string }) {
  return <article className="border border-[#d1dfd8] bg-[var(--surface)] p-6"><div className="flex h-11 w-11 items-center justify-center bg-[#2563eb] text-white"><Icon className="h-5 w-5" /></div><h3 className="lt-heading-3 mt-7">{title}</h3><p className="lt-body-sm mt-3">{text}</p></article>;
}

function Principle({ icon: Icon, title, text }: { icon: LucideIcon; title: string; text: string }) {
  return <article className="flex gap-4 border-t border-[#d9e5df] pt-5"><Icon className="mt-0.5 h-5 w-5 shrink-0 text-[#2563eb]" /><div><h3 className="lt-heading-3">{title}</h3><p className="lt-body-sm mt-2">{text}</p></div></article>;
}
