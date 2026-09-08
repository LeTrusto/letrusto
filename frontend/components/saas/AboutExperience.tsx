"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowRight,
  BarChart3,
  Check,
  CheckCircle2,
  Code2,
  Eye,
  Gauge,
  HeartHandshake,
  MapPin,
  MousePointer2,
  ShieldCheck,
  Sparkles,
  Star,
  Users,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const steps = [
  { number: "01", title: "Connect your events", text: "Choose the customer moments that tell the clearest story for your business.", label: "Event stream connected", metric: "12,480", detail: "approved signals" },
  { number: "02", title: "Curate the experience", text: "Set the tone, placement, and visibility rules so proof feels like part of your product.", label: "Experience calibrated", metric: "98.4%", detail: "brand alignment" },
  { number: "03", title: "Learn and improve", text: "Watch the signal work, then refine what you show as your customer story grows.", label: "Momentum measured", metric: "+31%", detail: "engagement lift" },
];

const activities = [
  { label: "New purchase", name: "Aarav Mehta", location: "Mumbai", action: "just booked a strategy call", color: "#d4af37" },
  { label: "5-star review", name: "Rohan Kapoor", location: "New Delhi", action: "left a 5-star review", color: "#57d6a1" },
  { label: "Live visitor", name: "Mira Shah", location: "Bengaluru", action: "started a free trial", color: "#91a7ff" },
];

const themes = {
  luxury: { label: "Dark luxury", panel: "bg-[#171b25]/90", border: "border-[#d4af37]/40", accent: "#d4af37", text: "text-[#f3e5ab]" },
  glass: { label: "Light glass", panel: "bg-white/10", border: "border-white/20", accent: "#57d6a1", text: "text-[#b9f5dc]" },
  minimal: { label: "Minimal", panel: "bg-[#10141d]", border: "border-white/10", accent: "#91a7ff", text: "text-[#dbe2ff]" },
} as const;

type ThemeKey = keyof typeof themes;

export default function AboutExperience() {
  const [theme, setTheme] = useState<ThemeKey>("luxury");
  const [activity, setActivity] = useState(0);
  const [activeStep, setActiveStep] = useState(0);
  const [pointer, setPointer] = useState({ x: 50, y: 20 });

  useEffect(() => {
    const handlePointer = (event: PointerEvent) => {
      setPointer({ x: (event.clientX / window.innerWidth) * 100, y: (event.clientY / window.innerHeight) * 100 });
    };
    window.addEventListener("pointermove", handlePointer);
    return () => window.removeEventListener("pointermove", handlePointer);
  }, []);

  const step = steps[activeStep];

  return (
    <main className="overflow-hidden bg-[#0a0d14] text-[#f7f4ed]">
      <section className="relative border-b border-white/10 bg-[#0a0d14]">
        <div className="pointer-events-none absolute inset-0 opacity-80" style={{ background: `radial-gradient(circle at ${pointer.x}% ${pointer.y}%, rgba(212,175,55,0.16), transparent 28%), radial-gradient(circle at 12% 72%, rgba(47,188,145,0.11), transparent 32%), linear-gradient(135deg, #0a0d14 0%, #101521 48%, #0b0f17 100%)` }} />
        <div className="pointer-events-none absolute inset-0 opacity-[0.08] [background-image:linear-gradient(rgba(255,255,255,0.15)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.15)_1px,transparent_1px)] [background-size:72px_72px] [mask-image:linear-gradient(to_bottom,black,transparent_82%)]" />
        <div className="relative mx-auto grid max-w-7xl items-center gap-14 px-5 py-20 sm:px-8 sm:py-28 lg:grid-cols-[0.95fr_1.05fr] lg:gap-20 lg:px-12">
          <div>
            <p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.28em] text-[#d4af37]"><Sparkles className="h-3.5 w-3.5" /> About LeTrusto</p>
            <h1 className="mt-6 max-w-3xl text-5xl font-black leading-[0.94] tracking-[-0.045em] text-white sm:text-7xl">Make trust easier to <span className="bg-gradient-to-r from-white via-[#f3e5ab] to-[#d4af37] bg-clip-text text-transparent">see.</span></h1>
            <p className="mt-7 max-w-xl text-base leading-8 text-[#a8b1c1] sm:text-lg">LeTrusto turns real customer activity into a clear, timely signal that gives the next visitor a reason to move.</p>
            <div className="mt-9 flex flex-wrap gap-3"><Link href="/register" className="lt-btn lt-btn-md border border-[#d4af37]/60 bg-[#d4af37] text-[#0a0d14] shadow-[0_0_30px_rgba(212,175,55,0.18)] hover:bg-[#f3e5ab]">Start building <ArrowRight className="h-4 w-4" /></Link><Link href="/how-it-works" className="lt-btn lt-btn-md border border-white/15 bg-white/[0.04] text-white backdrop-blur-md hover:border-[#d4af37]/60 hover:text-[#f3e5ab]">Explore the system</Link></div>
            <div className="mt-8 flex items-center gap-3 text-xs text-[#778296]"><span className="h-2 w-2 animate-pulse rounded-full bg-[#57d6a1]" /> Real signals. Carefully surfaced.</div>
          </div>
          <PreviewPanel theme={theme} setTheme={setTheme} activity={activity} setActivity={setActivity} compact />
        </div>
      </section>

      <section className="relative border-b border-white/10 bg-[#0d111a] px-5 py-24 sm:px-8 lg:px-12 lg:py-32"><div className="mx-auto max-w-7xl"><div className="grid gap-14 lg:grid-cols-[0.75fr_1.25fr] lg:items-start"><div><p className="eyebrow">Our mission</p><h2 className="mt-4 max-w-md text-3xl font-black tracking-[-0.03em] text-white sm:text-5xl">Confidence should be part of the experience.</h2></div><div className="space-y-5 text-base leading-8 text-[#9da7b8]"><p>People make better decisions when they can see evidence from people like them. Businesses deserve a simple way to make that evidence useful without interrupting the experience they have worked hard to create.</p><p>We are building the trust layer for modern customer journeys: lightweight enough to install quickly, thoughtful enough to feel native, and transparent enough for teams to stay in control.</p></div></div><div className="mt-16 grid gap-4 md:grid-cols-3"><ValueCard icon={Users} title="Human signals" text="Bring real activity, reviews, and customer stories into the moments where they matter." /><ValueCard icon={Gauge} title="Useful by default" text="Keep the setup focused, the controls practical, and the signal easy to understand." /><ValueCard icon={Eye} title="Visible impact" text="Give teams a clear view of what is being shown and how their audience responds." /></div></div></section>

      <section className="border-b border-white/10 bg-[#0a0d14] px-5 py-24 sm:px-8 lg:px-12 lg:py-32"><div className="mx-auto max-w-7xl"><div className="max-w-2xl"><p className="eyebrow">The product</p><h2 className="mt-4 text-3xl font-black tracking-[-0.03em] text-white sm:text-5xl">A calm, capable home for customer proof.</h2><p className="mt-5 text-base leading-8 text-[#9da7b8]">LeTrusto brings collection, curation, and display into one workspace, so your team can spend less time stitching tools together and more time serving customers.</p></div><div className="mt-14 grid gap-4 lg:grid-cols-3"><ProductCard icon={Zap} title="Live activity" text="Show recent signups, bookings, and purchases as a quiet rhythm of momentum." /><ProductCard icon={HeartHandshake} title="Customer stories" text="Collect and curate the words that sound like your future customers." /><ProductCard icon={Code2} title="Lightweight embeds" text="Install a focused widget with one script and control its behavior from your workspace." /></div></div></section>

      <section className="border-b border-white/10 bg-[#0d111a] px-5 py-24 sm:px-8 lg:px-12 lg:py-32"><div className="mx-auto grid max-w-7xl gap-14 lg:grid-cols-[0.72fr_1.28fr] lg:items-start"><div><p className="eyebrow">How it works</p><h2 className="mt-4 text-3xl font-black tracking-[-0.03em] text-white sm:text-5xl">From customer moment to meaningful signal.</h2><div className="mt-10 space-y-3">{steps.map((item, index) => <button key={item.number} type="button" onClick={() => setActiveStep(index)} className={`group flex w-full gap-4 border-l text-left transition-all ${activeStep === index ? "border-[#d4af37]" : "border-white/10 hover:border-white/30"}`}><span className={`ml-[-1px] flex h-10 w-12 shrink-0 items-center justify-center text-xs font-bold ${activeStep === index ? "bg-[#d4af37] text-[#0a0d14]" : "bg-white/[0.04] text-[#778296]"}`}>{item.number}</span><span className="pb-7 pt-1"><span className={`block text-base font-bold ${activeStep === index ? "text-[#f3e5ab]" : "text-white"}`}>{item.title}</span><span className="mt-2 block text-sm leading-6 text-[#778296]">{item.text}</span></span></button>)}</div></div><div className="lg:sticky lg:top-24"><div className="mb-4 flex items-center justify-between"><span className="eyebrow">Interactive workspace</span><span className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-[#778296]"><MousePointer2 className="h-3.5 w-3.5" /> Select a step</span></div><div className="border border-white/10 bg-white/[0.03] p-3 shadow-[0_24px_80px_rgba(0,0,0,0.35)] backdrop-blur-xl"><PreviewPanel theme={theme} setTheme={setTheme} activity={activity} setActivity={setActivity} step={step} /></div></div></div></section>

      <section className="border-b border-white/10 bg-[#0a0d14] px-5 py-24 sm:px-8 lg:px-12 lg:py-32"><div className="mx-auto max-w-7xl"><div className="max-w-2xl"><p className="eyebrow">Our trust principles</p><h2 className="mt-4 text-3xl font-black tracking-[-0.03em] text-white sm:text-5xl">The standard behind every signal.</h2></div><div className="mt-14 grid gap-4 md:grid-cols-2"><Principle icon={ShieldCheck} title="Evidence over theatre" text="We favor useful, recognizable customer signals over noise, inflated claims, or attention for its own sake." /><Principle icon={HeartHandshake} title="Respect the customer" text="The customer experience comes first. Proof should help people decide, never pressure them into a decision." /><Principle icon={Check} title="Control stays with you" text="Your team chooses what is approved, what is visible, and how the experience fits your brand." /><Principle icon={Sparkles} title="Keep improving" text="The best trust experience is never finished. We build for learning, iteration, and steady progress." /></div></div></section>

      <section className="relative overflow-hidden bg-[#0a0d14] px-5 py-24 sm:px-8 lg:px-12 lg:py-32"><div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(212,175,55,0.18),transparent_28%),linear-gradient(115deg,transparent_30%,rgba(212,175,55,0.08)_50%,transparent_70%)]" /><div className="relative mx-auto max-w-4xl border border-[#d4af37]/30 bg-white/[0.035] p-8 text-center shadow-[0_0_80px_rgba(212,175,55,0.08)] backdrop-blur-xl sm:p-16"><p className="eyebrow">Build trust into the next step</p><h2 className="mx-auto mt-5 max-w-3xl bg-gradient-to-r from-white to-[#d4af37] bg-clip-text text-3xl font-black tracking-[-0.03em] text-transparent sm:text-5xl">Your next customer is already looking for a reason to believe.</h2><p className="mx-auto mt-5 max-w-xl text-sm leading-7 text-[#9da7b8]">Give them a clear signal with a LeTrusto widget built around the way your business earns confidence.</p><Link href="/register" className="lt-btn lt-btn-md mt-9 border border-[#d4af37] bg-[#d4af37] text-[#0a0d14] shadow-[0_0_26px_rgba(212,175,55,0.2)] transition-shadow hover:bg-[#f3e5ab] hover:shadow-[0_0_38px_rgba(212,175,55,0.42)]">Create your free workspace <ArrowRight className="h-4 w-4" /></Link></div></section>

      <style jsx>{`.eyebrow{font-size:10px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:#d4af37}.glass-card{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.1);backdrop-filter:blur(16px)}`}</style>
    </main>
  );
}

function PreviewPanel({ theme, setTheme, activity, setActivity, step, compact = false }: { theme: ThemeKey; setTheme: (theme: ThemeKey) => void; activity: number; setActivity: (activity: number) => void; step?: (typeof steps)[number]; compact?: boolean }) {
  const currentTheme = themes[theme];
  const item = activities[activity];
  return <div className={`relative overflow-hidden border ${currentTheme.border} ${currentTheme.panel} p-4 shadow-[0_22px_70px_rgba(0,0,0,0.28)] backdrop-blur-xl ${compact ? "min-h-[340px]" : "min-h-[470px]"}`}><div className="absolute inset-0 bg-[radial-gradient(circle_at_75%_20%,rgba(212,175,55,0.16),transparent_26%),linear-gradient(135deg,rgba(255,255,255,0.04),transparent_55%)]" /><div className="relative flex items-center justify-between border-b border-white/10 pb-4"><div><p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#778296]">LeTrusto / Trust Studio</p><p className="mt-1 text-sm font-bold text-white">{step?.label || "Live proof preview"}</p></div><span className="flex items-center gap-2 text-[10px] uppercase tracking-[0.15em] text-[#57d6a1]"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[#57d6a1]" /> Live</span></div>{step && <div className="relative mt-5 flex items-end justify-between"><div><p className="text-4xl font-black text-white">{step.metric}</p><p className="mt-1 text-xs text-[#778296]">{step.detail}</p></div><BarChart3 className="h-8 w-8" style={{ color: currentTheme.accent }} /></div>}<div className={`relative flex ${compact ? "min-h-[190px]" : "min-h-[285px]"} items-center justify-center py-8`}><AnimatePresence mode="wait"><motion.div key={`${item.name}-${theme}-${step?.number || "hero"}`} initial={{ opacity: 0, y: 16, rotate: -2 }} animate={{ opacity: 1, y: 0, rotate: 0 }} exit={{ opacity: 0, y: -12 }} transition={{ duration: 0.35 }} className="w-full max-w-[330px] border border-white/10 bg-[#0d111a]/90 p-4 shadow-[0_18px_55px_rgba(0,0,0,0.4)]" style={{ borderLeft: `3px solid ${currentTheme.accent}` }}><div className="flex items-start gap-3"><div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xs font-black text-[#0a0d14]" style={{ backgroundColor: item.color }}>{item.name.split(" ").map((part) => part[0]).join("")}</div><div className="min-w-0"><div className="flex items-center gap-1 text-sm font-bold text-white">{item.name}<CheckCircle2 className="h-3.5 w-3.5" style={{ color: currentTheme.accent }} /></div><div className="mt-1 flex items-center gap-1 text-xs text-[#778296]"><MapPin className="h-3 w-3" />{item.location}</div><p className="mt-2 text-sm leading-5 text-[#c4cad5]">{item.action}</p><div className={`mt-2 flex items-center gap-1 text-xs font-bold ${currentTheme.text}`}><Star className="h-3.5 w-3.5 fill-current" /> Trusted by real customers</div></div></div></motion.div></AnimatePresence></div><div className="relative flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-4"><div className="flex gap-1.5">{Object.entries(themes).map(([key, value]) => <button key={key} type="button" onClick={() => setTheme(key as ThemeKey)} className={`px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider transition ${theme === key ? "border border-white/20 bg-white/10 text-white" : "text-[#778296] hover:text-white"}`}>{value.label}</button>)}</div>{compact ? <span className="text-[10px] text-[#778296]">{item.label}</span> : <div className="flex gap-1.5">{activities.map((activityItem, index) => <button key={activityItem.label} type="button" aria-label={`Show ${activityItem.label}`} onClick={() => setActivity(index)} className={`h-2 w-2 rounded-full transition ${activity === index ? "scale-125 bg-[#d4af37]" : "bg-white/20 hover:bg-white/50"}`} />)}</div>}</div></div>;
}

function ValueCard({ icon: Icon, title, text }: { icon: typeof Users; title: string; text: string }) {
  return <motion.article whileHover={{ y: -5 }} className="glass-card group p-6 transition-colors hover:border-[#d4af37]/50"><div className="flex h-11 w-11 items-center justify-center border border-[#d4af37]/30 bg-[#d4af37]/10 text-[#f3e5ab] transition-colors group-hover:bg-[#d4af37] group-hover:text-[#0a0d14]"><Icon className="h-5 w-5" /></div><h3 className="mt-7 text-lg font-bold text-white">{title}</h3><p className="mt-3 text-sm leading-7 text-[#9da7b8]">{text}</p></motion.article>;
}

function ProductCard({ icon: Icon, title, text }: { icon: typeof Zap; title: string; text: string }) {
  return <motion.article whileHover={{ y: -5 }} className="glass-card group p-6 transition-colors hover:border-[#d4af37]/50"><div className="flex h-11 w-11 items-center justify-center bg-[#d4af37]/10 text-[#d4af37]"><Icon className="h-5 w-5" /></div><h3 className="mt-7 text-lg font-bold text-white">{title}</h3><p className="mt-3 text-sm leading-7 text-[#9da7b8]">{text}</p></motion.article>;
}

function Principle({ icon: Icon, title, text }: { icon: typeof ShieldCheck; title: string; text: string }) {
  return <motion.article whileHover={{ y: -4 }} className="glass-card group flex gap-4 p-6 transition-colors hover:border-[#d4af37]/50"><Icon className="mt-0.5 h-5 w-5 shrink-0 text-[#d4af37] transition-transform group-hover:scale-110" /><div><h3 className="text-base font-bold text-white">{title}</h3><p className="mt-2 text-sm leading-7 text-[#9da7b8]">{text}</p></div></motion.article>;
}
