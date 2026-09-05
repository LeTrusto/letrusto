"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowRight,
  Check,
  ChevronDown,
  Code2,
  Grid2X2,
  MessageCircleHeart,
  Play,
  ShieldCheck,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import LiveProofPreview from "@/components/saas/LiveProofPreview";

const plans = [
  { name: "Free", price: "₹0", description: "A clean first signal for growing teams.", features: ["1 widget", "1,000 views / month", "Live sales popups"], action: "Start free", featured: false },
  { name: "Starter", price: "₹999", description: "The trust layer for an active storefront.", features: ["3 widgets", "10,000 views / month", "Custom colors", "Review collection"], action: "Start trial", featured: true },
  { name: "Pro", price: "₹2,499", description: "Every proof format, ready to compound.", features: ["Unlimited widgets", "Unlimited views", "Video reviews", "Priority support"], action: "Go Pro", featured: false },
];

const faqs = [
  ["Can I try LeTrusto before paying?", "Yes. The Free plan gives you one widget and 1,000 monthly views with no card required."],
  ["Where does the widget appear?", "Paste one lightweight script tag into your site. You control the position, color, delay, and approved events from Trust Studio."],
  ["Can I collect reviews as well as show popups?", "Yes. Starter and Pro are designed for both live activity and structured review collection."],
  ["How does billing work?", "Paid plans renew monthly through Razorpay subscriptions. You can manage the plan from your LeTrusto workspace."],
];

export default function SaaSLanding() {
  const [openFaq, setOpenFaq] = useState(0);

  return (
    <main className="overflow-hidden bg-[#f7faf8] text-[#17382e]">
      <section className="relative border-b border-[#d9e5df] bg-[#17382e] text-[#f7faf8]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_20%,rgba(37,99,235,0.35),transparent_28%),radial-gradient(circle_at_15%_70%,rgba(20,184,166,0.2),transparent_30%)]" />
        <div className="relative mx-auto grid max-w-7xl items-center gap-12 px-5 pb-20 pt-16 sm:px-8 sm:pb-28 lg:grid-cols-[1.05fr_0.95fr] lg:gap-20 lg:px-12">
          <div>
            <p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.24em] text-[#60a5fa]"><ShieldCheck className="h-3.5 w-3.5" /> Social proof, made visible</p>
            <h1 className="mt-5 max-w-3xl text-5xl font-black leading-[0.98] tracking-[-0.04em] sm:text-7xl">Turn quiet confidence into <span className="text-[#60a5fa]">visible momentum.</span></h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-[#c5d7cf] sm:text-lg">LeTrusto helps ambitious businesses show the right customer story at the right moment, without slowing down their site.</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/register" className="flex items-center gap-2 bg-[#2563eb] px-5 py-3.5 text-sm font-bold text-white transition hover:bg-blue-500">Start Free Trial <ArrowRight className="h-4 w-4" /></Link>
              <a href="#demo" className="flex items-center gap-2 border border-[#638378] px-5 py-3.5 text-sm font-bold text-white hover:border-[#60a5fa]"><Play className="h-4 w-4 fill-current" /> Live Demo</a>
            </div>
            <p className="mt-5 text-xs text-[#9bb4a8]">No credit card required. Install in minutes.</p>
          </div>
          <div id="demo" className="border border-[#638378] bg-[#22483c] p-3 shadow-[0_24px_70px_rgba(0,0,0,0.2)]"><LiveProofPreview color="#2563eb" /></div>
        </div>
      </section>

      <section id="features" className="mx-auto max-w-7xl px-5 py-20 sm:px-8 lg:px-12 lg:py-28">
        <div className="max-w-2xl"><p className="eyebrow">A calmer conversion layer</p><h2 className="mt-3 text-3xl font-black tracking-tight sm:text-5xl">Proof that works while you do.</h2><p className="mt-5 text-base leading-7 text-[#587268]">Move beyond generic badges. Give every visitor a reason to believe the next step is worth taking.</p></div>
        <div className="mt-12 grid gap-5 md:grid-cols-3"><Feature icon={Zap} title="Live Sales Popups" text="Turn recent purchases, signups, and bookings into a quiet rhythm of confidence." accent="#2563eb" /><Feature icon={Grid2X2} title="Wall of Love grids" text="Bring your best customer stories together in a proof library your team can curate." accent="#0f766e" /><Feature icon={MessageCircleHeart} title="Review Collection" text="Capture useful feedback and surface the words that sound like your future customers." accent="#e11d48" /></div>
      </section>

      <section id="pricing" className="border-y border-[#d9e5df] bg-[#edf5f1] px-5 py-20 sm:px-8 lg:px-12 lg:py-28">
        <div className="mx-auto max-w-7xl"><div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><p className="eyebrow">Simple by design</p><h2 className="mt-3 text-3xl font-black tracking-tight sm:text-5xl">Start small. Scale when proof compounds.</h2></div><p className="max-w-xs text-sm leading-6 text-[#587268]">All plans include the lightweight embed and a human-readable event stream.</p></div>
          <div className="mt-12 grid gap-4 lg:grid-cols-3">{plans.map((plan) => <article key={plan.name} className={`relative flex flex-col border p-6 ${plan.featured ? "border-[#2563eb] bg-[#f7fbff] shadow-[0_18px_45px_rgba(37,99,235,0.12)]" : "border-[#d1dfd8] bg-[#fbfdfc]"}`}><div className="flex items-center justify-between"><h3 className="text-lg font-black">{plan.name}</h3>{plan.featured && <span className="bg-[#2563eb] px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-white">Popular</span>}</div><p className="mt-5 text-4xl font-black">{plan.price}<span className="text-sm font-medium text-[#71877f]"> / month</span></p><p className="mt-5 min-h-10 text-sm leading-5 text-[#587268]">{plan.description}</p><ul className="mt-6 flex-1 space-y-3 border-t border-[#d9e5df] pt-5">{plan.features.map((feature) => <li key={feature} className="flex items-center gap-2 text-sm text-[#39564c]"><Check className="h-3.5 w-3.5 text-[#2563eb]" />{feature}</li>)}</ul><Link href={plan.name === "Free" ? "/register" : `/register?plan=${plan.name.toLowerCase()}`} className={`mt-8 flex items-center justify-center gap-2 px-4 py-3 text-sm font-bold ${plan.featured ? "bg-[#2563eb] text-white hover:bg-blue-600" : "border border-[#17382e] text-[#17382e] hover:bg-[#17382e] hover:text-white"}`}>{plan.action}<ArrowRight className="h-4 w-4" /></Link></article>)}</div>
        </div>
      </section>

      <section id="faq" className="mx-auto max-w-3xl px-5 py-20 sm:px-8 lg:py-28"><div className="text-center"><p className="eyebrow">Questions, answered</p><h2 className="mt-3 text-3xl font-black tracking-tight sm:text-5xl">No mystery in the machinery.</h2></div><div className="mt-10 divide-y divide-[#d9e5df] border-y border-[#d9e5df]">{faqs.map(([question, answer], index) => <div key={question}><button type="button" onClick={() => setOpenFaq(openFaq === index ? -1 : index)} className="flex w-full items-center justify-between gap-5 py-5 text-left text-sm font-bold"><span>{question}</span><ChevronDown className={`h-4 w-4 shrink-0 transition-transform ${openFaq === index ? "rotate-180 text-[#2563eb]" : "text-[#71877f]"}`} /></button><AnimatePresence initial={false}>{openFaq === index && <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden"><p className="max-w-2xl pb-5 pr-8 text-sm leading-6 text-[#587268]">{answer}</p></motion.div>}</AnimatePresence></div>)}</div><div className="mt-16 border border-[#17382e] bg-[#17382e] p-8 text-center text-white sm:p-12"><Code2 className="mx-auto h-7 w-7 text-[#60a5fa]" /><h2 className="mt-4 text-2xl font-black">Your next best customer is already looking.</h2><p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-[#c5d7cf]">Give them the signal they need to take the next step.</p><Link href="/register" className="mt-6 inline-flex items-center gap-2 bg-[#2563eb] px-5 py-3 text-sm font-bold text-white hover:bg-blue-500">Build your first widget <ArrowRight className="h-4 w-4" /></Link></div></section>
      <style jsx>{`.eyebrow{font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#2563eb}`}</style>
    </main>
  );
}

function Feature({ icon: Icon, title, text, accent }: { icon: typeof Zap; title: string; text: string; accent: string }) {
  return <motion.article whileHover={{ y: -4 }} className="border border-[#d9e5df] bg-white p-6"><div className="flex h-11 w-11 items-center justify-center text-white" style={{ backgroundColor: accent }}><Icon className="h-5 w-5" /></div><h3 className="mt-7 text-lg font-black">{title}</h3><p className="mt-3 text-sm leading-6 text-[#587268]">{text}</p></motion.article>;
}
