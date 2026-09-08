"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronDown,
  Code2,
  Grid2X2,
  MapPin,
  MessageCircleHeart,
  Play,
  ShieldCheck,
  Star,
  WalletCards,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const previewModes = [
  { label: "Live Sales Popup", icon: Zap, name: "Aarav Mehta", location: "Mumbai", action: "just booked a strategy call", accent: "#d4af37" },
  { label: "Wall of Love", icon: Grid2X2, name: "Mira Shah", location: "Bengaluru", action: "said LeTrusto made trust visible", accent: "#57d6a1" },
  { label: "Review Badge", icon: MessageCircleHeart, name: "Rohan Kapoor", location: "New Delhi", action: "left a 5-star review", accent: "#91a7ff" },
];

const plans = [
  { name: "Free", monthly: 0, description: "A considered first signal for growing teams.", features: ["1 widget", "1,000 views / month", "Live sales popups"], action: "Start free" },
  { name: "Starter", monthly: 999, description: "The trust layer for an active storefront.", features: ["3 widgets", "10,000 views / month", "Custom colors", "Review collection"], action: "Start trial", featured: true },
  { name: "Pro", monthly: 2499, description: "Every proof format, ready to compound.", features: ["Unlimited widgets", "Unlimited views", "Video reviews", "Priority support"], action: "Go Pro" },
];

const faqs = [
  ["Can I try LeTrusto before paying?", "Yes. The Free plan gives you one widget and 1,000 monthly views with no card required."],
  ["Where does the widget appear?", "Paste one lightweight script tag into your site. You control position, color, delay, and approved events from Trust Studio."],
  ["Can I collect reviews as well as show popups?", "Yes. Starter and Pro are designed for both live activity and structured review collection."],
  ["How does billing work?", "Choose monthly or annual billing from your workspace. You can manage your plan from LeTrusto at any time."],
];

export default function SaaSLanding() {
  const [previewMode, setPreviewMode] = useState(0);
  const [currency, setCurrency] = useState<"INR" | "USD">("INR");
  const [annual, setAnnual] = useState(false);
  const [openFaq, setOpenFaq] = useState(0);
  const [pointer, setPointer] = useState({ x: 50, y: 20 });

  useEffect(() => {
    const onPointerMove = (event: PointerEvent) => setPointer({ x: (event.clientX / window.innerWidth) * 100, y: (event.clientY / window.innerHeight) * 100 });
    window.addEventListener("pointermove", onPointerMove);
    return () => window.removeEventListener("pointermove", onPointerMove);
  }, []);

  return (
    <main className="overflow-hidden bg-[#0a0d14] text-[#f7f4ed]">
      <section className="relative border-b border-white/10 bg-[#0a0d14]">
        <div className="pointer-events-none absolute inset-0" style={{ background: `radial-gradient(circle at ${pointer.x}% ${pointer.y}%, rgba(212,175,55,0.16), transparent 28%), radial-gradient(circle at 10% 72%, rgba(47,188,145,0.1), transparent 30%), linear-gradient(135deg,#0a0d14 0%,#111622 50%,#0a0d14 100%)` }} />
        <div className="pointer-events-none absolute inset-0 opacity-[0.08] [background-image:linear-gradient(rgba(255,255,255,0.15)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.15)_1px,transparent_1px)] [background-size:72px_72px] [mask-image:linear-gradient(to_bottom,black,transparent_85%)]" />
        <div className="relative mx-auto grid max-w-7xl items-center gap-14 px-5 pb-20 pt-16 sm:px-8 sm:pb-28 lg:grid-cols-[0.92fr_1.08fr] lg:gap-20 lg:px-12">
          <div><p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.28em] text-[#d4af37]"><ShieldCheck className="h-3.5 w-3.5" /> Social proof, made visible</p><h1 className="mt-6 max-w-3xl text-5xl font-black leading-[0.94] tracking-[-0.045em] text-white sm:text-7xl">Turn quiet confidence into <span className="bg-gradient-to-b from-white to-[#d4af37] bg-clip-text text-transparent">visible momentum.</span></h1><p className="mt-7 max-w-xl text-base leading-8 text-[#a8b1c1] sm:text-lg">LeTrusto helps ambitious businesses show the right customer story at the right moment, without slowing down their site.</p><div className="mt-9 flex flex-wrap gap-3"><Link href="/register" className="lt-btn lt-btn-md border border-[#d4af37]/60 bg-[#d4af37] text-[#0a0d14] shadow-[0_0_30px_rgba(212,175,55,0.18)] hover:bg-[#f3e5ab]">Start free <ArrowRight className="h-4 w-4" /></Link><a href="#demo" className="lt-btn lt-btn-md border border-white/15 bg-white/[0.04] text-white backdrop-blur-md hover:border-[#d4af37]/60 hover:text-[#f3e5ab]"><Play className="h-4 w-4 fill-current" /> Live demo</a></div><p className="mt-7 text-xs text-[#778296]">No card required. Install in minutes.</p></div>
          <div id="demo"><Sandbox mode={previewMode} setMode={setPreviewMode} /></div>
        </div>
      </section>

      <section id="features" className="border-b border-white/10 bg-[#0d111a] px-5 py-20 sm:px-8 lg:px-12 lg:py-28"><div className="mx-auto max-w-7xl"><div className="max-w-2xl"><p className="eyebrow">A calmer conversion layer</p><h2 className="mt-4 text-3xl font-black tracking-[-0.03em] text-white sm:text-5xl">Proof that works while you do.</h2><p className="mt-5 text-base leading-8 text-[#9da7b8]">Move beyond generic badges. Give every visitor a reason to believe the next step is worth taking.</p></div><div className="mt-14 grid gap-4 lg:grid-cols-3"><Feature icon={Zap} title="Live Sales Popups" text="Turn recent purchases, signups, and bookings into a quiet rhythm of confidence." kind="popup" /><Feature icon={Grid2X2} title="Wall of Love grids" text="Bring your best customer stories together in a proof library your team can curate." kind="wall" /><Feature icon={MessageCircleHeart} title="Review Collection" text="Capture useful feedback and surface the words that sound like your future customers." kind="review" /></div></div></section>

      <section id="pricing" className="border-b border-white/10 bg-[#0a0d14] px-5 py-20 sm:px-8 lg:px-12 lg:py-28"><div className="mx-auto max-w-7xl"><div className="flex flex-col justify-between gap-8 sm:flex-row sm:items-end"><div><p className="eyebrow">Simple by design</p><h2 className="mt-4 text-3xl font-black tracking-[-0.03em] text-white sm:text-5xl">Start small. Scale when proof compounds.</h2></div><div className="flex flex-wrap items-center gap-2 border border-white/10 bg-white/[0.03] p-1 text-xs font-bold"><button type="button" onClick={() => setAnnual(false)} className={`px-3 py-2 ${!annual ? "bg-white/10 text-white" : "text-[#778296]"}`}>Monthly</button><button type="button" onClick={() => setAnnual(true)} className={`px-3 py-2 ${annual ? "bg-white/10 text-white" : "text-[#778296]"}`}>Annual</button><span className="px-2 text-[#d4af37]">Save 20%</span></div></div><div className="mt-5 flex items-center gap-2 text-xs text-[#778296]"><WalletCards className="h-3.5 w-3.5" /> Display currency <button type="button" onClick={() => setCurrency("INR")} className={currency === "INR" ? "font-bold text-[#f3e5ab]" : "hover:text-white"}>₹ INR</button><span>/</span><button type="button" onClick={() => setCurrency("USD")} className={currency === "USD" ? "font-bold text-[#f3e5ab]" : "hover:text-white"}>$ USD</button></div><div className="mt-12 grid gap-4 lg:grid-cols-3">{plans.map((plan) => <PlanCard key={plan.name} plan={plan} annual={annual} currency={currency} />)}</div></div></section>

      <section id="faq" className="border-b border-white/10 bg-[#0d111a] px-5 py-20 sm:px-8 lg:px-12 lg:py-28"><div className="mx-auto max-w-3xl"><div className="text-center"><p className="eyebrow">Questions, answered</p><h2 className="mt-4 text-3xl font-black tracking-[-0.03em] text-white sm:text-5xl">No mystery in the machinery.</h2></div><div className="mt-12 divide-y divide-white/10 border-y border-white/10">{faqs.map(([question, answer], index) => <div key={question}><button type="button" onClick={() => setOpenFaq(openFaq === index ? -1 : index)} className={`flex w-full items-center justify-between gap-5 py-6 text-left text-sm font-bold transition-colors ${openFaq === index ? "text-[#f3e5ab]" : "text-white hover:text-[#f3e5ab]"}`}><span>{question}</span><ChevronDown className={`h-4 w-4 shrink-0 transition-transform ${openFaq === index ? "rotate-180 text-[#d4af37]" : "text-[#778296]"}`} /></button><AnimatePresence initial={false}>{openFaq === index && <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden"><p className="max-w-2xl pb-6 pr-8 text-sm leading-7 text-[#9da7b8]">{answer}</p></motion.div>}</AnimatePresence></div>)}</div><div className="relative mt-20 overflow-hidden border border-[#d4af37]/30 bg-white/[0.035] p-8 text-center shadow-[0_0_80px_rgba(212,175,55,0.08)] backdrop-blur-xl sm:p-14"><div className="pointer-events-none absolute inset-0 opacity-40 [background-image:linear-gradient(rgba(212,175,55,0.16)_1px,transparent_1px),linear-gradient(90deg,rgba(212,175,55,0.16)_1px,transparent_1px)] [background-size:54px_54px]" /><Code2 className="relative mx-auto h-7 w-7 text-[#d4af37]" /><h2 className="relative mt-5 bg-gradient-to-r from-white to-[#d4af37] bg-clip-text text-3xl font-black text-transparent sm:text-5xl">Your next best customer is already looking.</h2><p className="relative mx-auto mt-4 max-w-lg text-sm leading-7 text-[#9da7b8]">Give them the signal they need to take the next step.</p><Link href="/register" className="relative lt-btn lt-btn-md mt-8 border border-[#d4af37] bg-[#d4af37] text-[#0a0d14] shadow-[0_0_26px_rgba(212,175,55,0.2)] hover:bg-[#f3e5ab] hover:shadow-[0_0_38px_rgba(212,175,55,0.42)]">Build your first widget <ArrowRight className="h-4 w-4" /></Link></div></div></section>
      <style jsx>{`.eyebrow{font-size:10px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:#d4af37}.glass-card{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.1);backdrop-filter:blur(16px)}`}</style>
    </main>
  );
}

function Sandbox({ mode, setMode }: { mode: number; setMode: (mode: number) => void }) {
  const selected = previewModes[mode];
  const [pulse, setPulse] = useState(0);
  useEffect(() => { const timer = window.setInterval(() => setPulse((value) => value + 1), 4000); return () => window.clearInterval(timer); }, []);
  return <div className="glass-card relative overflow-hidden p-3 shadow-[0_24px_90px_rgba(0,0,0,0.38)]"><div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_18%,rgba(212,175,55,0.18),transparent_28%),linear-gradient(135deg,rgba(255,255,255,0.06),transparent_58%)]" /><div className="relative flex flex-wrap gap-1 border-b border-white/10 pb-3">{previewModes.map((item, index) => { const Icon = item.icon; return <button key={item.label} type="button" onClick={() => setMode(index)} className={`flex items-center gap-2 px-3 py-2 text-[10px] font-bold transition ${mode === index ? "bg-[#d4af37] text-[#0a0d14]" : "text-[#778296] hover:bg-white/10 hover:text-white"}`}><Icon className="h-3.5 w-3.5" />{item.label}</button>; })}</div><div className="relative flex min-h-[365px] items-center justify-center p-5"><AnimatePresence mode="wait"><motion.div key={`${selected.name}-${pulse}`} initial={{ opacity: 0, y: 20, rotate: -2 }} animate={{ opacity: 1, y: 0, rotate: 0 }} exit={{ opacity: 0, y: -16 }} className="w-full max-w-[350px] border border-white/10 bg-[#0d111a]/90 p-5 shadow-[0_22px_60px_rgba(0,0,0,0.45)]" style={{ borderLeft: `3px solid ${selected.accent}` }}><div className="flex items-center justify-between"><span className="flex items-center gap-2 text-[10px] uppercase tracking-[0.18em] text-[#778296]"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[#57d6a1]" /> Live sandbox</span><span className="text-[10px] text-[#778296]">{selected.label}</span></div><div className="mt-7 flex items-start gap-3"><div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-black text-[#0a0d14]" style={{ backgroundColor: selected.accent }}>{selected.name.split(" ").map((part) => part[0]).join("")}</div><div><div className="flex items-center gap-1 text-sm font-bold text-white">{selected.name}<CheckCircle2 className="h-3.5 w-3.5" style={{ color: selected.accent }} /></div><div className="mt-1 flex items-center gap-1 text-xs text-[#778296]"><MapPin className="h-3 w-3" />{selected.location}</div><p className="mt-3 text-sm leading-6 text-[#c4cad5]">{selected.action}</p><div className="mt-3 flex items-center gap-1 text-xs font-bold" style={{ color: selected.accent }}><Star className="h-3.5 w-3.5 fill-current" /> Trusted by real customers</div></div></div></motion.div></AnimatePresence></div><div className="relative flex items-center justify-between border-t border-white/10 pt-3 text-[10px] text-[#778296]"><span>Auto-refreshes every 4 seconds</span><span className="flex gap-1">{previewModes.map((item, index) => <button key={item.label} type="button" aria-label={`Preview ${item.label}`} onClick={() => setMode(index)} className={`h-1.5 w-1.5 rounded-full ${mode === index ? "bg-[#d4af37]" : "bg-white/20"}`} />)}</span></div></div>;
}

function Feature({ icon: Icon, title, text, kind }: { icon: typeof Zap; title: string; text: string; kind: "popup" | "wall" | "review" }) {
  return <motion.article whileHover={{ y: -6 }} className="glass-card group min-h-[280px] p-6 transition-colors hover:border-[#d4af37]/50 hover:shadow-[0_0_25px_rgba(212,175,55,0.15)]"><div className="flex h-11 w-11 items-center justify-center bg-[#d4af37]/10 text-[#d4af37]"><Icon className="h-5 w-5" /></div><h3 className="mt-7 text-lg font-bold text-white">{title}</h3><p className="mt-3 text-sm leading-7 text-[#9da7b8]">{text}</p><FeatureDemo kind={kind} /></motion.article>;
}

function FeatureDemo({ kind }: { kind: "popup" | "wall" | "review" }) {
  if (kind === "wall") return <div className="mt-6 grid grid-cols-3 gap-2 opacity-80 transition-opacity group-hover:opacity-100">{["AM", "RS", "MK"].map((initials) => <div key={initials} className="border border-white/10 bg-white/[0.04] p-2 text-center text-[10px] text-[#d4af37]"><div className="mx-auto h-5 w-5 rounded-full bg-[#57d6a1]/70" />{initials}</div>)}</div>;
  if (kind === "review") return <div className="mt-6 flex items-center gap-1 text-[#d4af37] transition-transform group-hover:scale-105">{[1, 2, 3, 4, 5].map((star) => <Star key={star} className="h-4 w-4 fill-current" />)}<span className="ml-2 text-xs text-[#778296]">4.9 / 5</span></div>;
  return <div className="mt-6 flex items-center gap-3 border border-white/10 bg-white/[0.04] p-3 opacity-80 transition-transform group-hover:translate-x-1"><span className="h-2 w-2 animate-pulse rounded-full bg-[#d4af37]" /><span className="text-xs text-[#c4cad5]">Mira just joined</span><CheckCircle2 className="ml-auto h-3.5 w-3.5 text-[#57d6a1]" /></div>;
}

function PlanCard({ plan, annual, currency }: { plan: (typeof plans)[number]; annual: boolean; currency: "INR" | "USD" }) {
  const price = annual ? Math.round(plan.monthly * 0.8) : plan.monthly;
  const displayPrice = currency === "USD" ? Math.round(price / 83) : price;
  const symbol = currency === "USD" ? "$" : "₹";
  return <article className={`relative flex flex-col border p-6 backdrop-blur-xl ${plan.featured ? "border-[#d4af37]/70 bg-[#191710]/80 shadow-[0_0_35px_rgba(212,175,55,0.14)]" : "glass-card"}`}>{plan.featured && <span className="absolute right-5 top-5 bg-[#d4af37] px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-[#0a0d14]">Popular</span>}<h3 className="text-lg font-bold text-white">{plan.name}</h3><p className="mt-6 text-4xl font-black text-white">{symbol}{displayPrice.toLocaleString()}<span className="text-sm font-medium text-[#778296]"> / month</span></p><p className="mt-5 min-h-10 text-sm leading-6 text-[#9da7b8]">{plan.description}</p><ul className="mt-6 flex-1 space-y-3 border-t border-white/10 pt-5">{plan.features.map((feature) => <li key={feature} className="flex items-center gap-2 text-sm text-[#c4cad5]"><Check className="h-3.5 w-3.5 text-[#d4af37]" />{feature}</li>)}</ul><Link href={plan.name === "Free" ? "/register" : `/register?plan=${plan.name.toLowerCase()}`} className={`mt-8 flex items-center justify-center gap-2 px-4 py-3 text-sm font-bold ${plan.featured ? "bg-[#d4af37] text-[#0a0d14] hover:bg-[#f3e5ab]" : "border border-white/20 text-white hover:border-[#d4af37] hover:text-[#f3e5ab]"}`}>{plan.action}<ArrowRight className="h-4 w-4" /></Link></article>;
}
