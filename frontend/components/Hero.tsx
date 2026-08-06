"use client";

import { motion } from "framer-motion";
import { ArrowRight, Loader2, Search, Sparkles } from "lucide-react";
import Link from "next/link";
import { useRef, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

export default function Hero() {
  const [query, setQuery] = useState("");
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (isPending) return;

    const trimmed = query.trim();
    startTransition(() => {
      router.push(trimmed ? `/search?q=${encodeURIComponent(trimmed)}` : "/search");
    });
  }

  const chips = [
    "Best phone under 30000",
    "Laptop for coding",
    "Headphones for office",
    "Best web hosting",
  ];

  return (
    <section className="relative overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(168,85,247,0.16),_transparent_30%),radial-gradient(circle_at_85%_0%,_rgba(251,113,133,0.14),_transparent_28%),linear-gradient(180deg,#ffffff_0%,#fff7ed_100%)] py-16 md:py-22">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent" />
      <div className="pointer-events-none absolute -top-24 left-1/2 h-[440px] w-[440px] -translate-x-1/2 rounded-full bg-fuchsia-200/25 blur-3xl" />
      <div className="pointer-events-none absolute top-10 right-0 h-72 w-72 rounded-full bg-orange-100/40 blur-3xl" />
      <div className="pointer-events-none absolute -left-10 top-24 h-56 w-56 rounded-full bg-pink-100/30 blur-3xl" />

      <div className="relative mx-auto grid max-w-7xl gap-12 px-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
        <div>
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="-mx-2 mb-5 flex snap-x gap-2 overflow-x-auto px-2 pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          >
            {chips.map((chip, index) => (
              <button
                key={chip}
                type="button"
                disabled={isPending}
                onClick={() => {
                  if (isPending) return;
                  setQuery(chip);
                  startTransition(() => {
                    router.push(`/search?q=${encodeURIComponent(chip)}`);
                  });
                }}
                className="group shrink-0 snap-start rounded-full border border-violet-200/80 bg-white/90 px-2.5 py-1 text-[11px] font-semibold tracking-[0.01em] text-slate-700 shadow-sm transition duration-300 hover:-translate-y-0.5 hover:border-pink-300 hover:shadow-md focus-visible:border-fuchsia-400 disabled:cursor-not-allowed disabled:opacity-60"
                style={{ transitionDelay: `${index * 20}ms` }}
              >
                <span className="bg-gradient-to-r from-violet-700 via-fuchsia-600 to-orange-500 bg-clip-text text-transparent group-hover:opacity-95">
                  {chip}
                </span>
              </button>
            ))}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.04 }}
            className="inline-flex w-fit items-center gap-2 rounded-full border border-violet-200 bg-white/90 px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm"
          >
            <Sparkles className="h-4 w-4 text-fuchsia-600" />
            Research-backed buying decisions
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.08 }}
            className="text-5xl font-black tracking-tight text-slate-950 md:text-7xl"
          >
            Know Before{" "}
            <span className="bg-gradient-to-r from-purple-600 via-pink-500 to-orange-500 bg-clip-text text-transparent">
              You Buy
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.16 }}
            className="mt-5 max-w-2xl text-lg leading-relaxed text-slate-600 md:text-xl"
          >
            LeTrusto helps shoppers compare products, understand trade-offs, and move from research to confident decisions with less noise.
          </motion.p>

          <motion.form
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.24 }}
            onSubmit={handleSearch}
            className="mt-8 overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-[0_24px_80px_-36px_rgba(15,23,42,0.28)] transition duration-300 focus-within:-translate-y-0.5 focus-within:border-fuchsia-300 focus-within:shadow-[0_30px_90px_-40px_rgba(139,92,246,0.35)]"
          >
            <div className="flex items-start gap-4 px-5 py-5">
              <div className="mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-fuchsia-50 text-fuchsia-700 transition-colors duration-300 focus-within:bg-fuchsia-100">
                <Search className="h-5 w-5" aria-hidden="true" />
              </div>
              <div className="flex-1">
                <label htmlFor="hero-search" className="sr-only">Search products, brands or ask a buying question</label>
                <textarea
                  id="hero-search"
                  ref={textareaRef}
                  rows={1}
                  disabled={isPending}
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  onInput={(event) => {
                    const target = event.currentTarget;
                    target.style.height = "0px";
                    target.style.height = `${Math.min(target.scrollHeight, 144)}px`;
                  }}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      event.currentTarget.form?.requestSubmit();
                    }
                  }}
                  aria-describedby="hero-search-hint"
                  placeholder="Search by budget, use-case, or product pair (e.g. phone under 30000, laptop for coding)..."
                  className="min-h-[36px] w-full resize-none bg-transparent text-base leading-7 text-slate-900 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-70 md:text-lg"
                />
                <p id="hero-search-hint" className="mt-2 text-sm text-slate-500">
                  Press Enter to search. Use Shift+Enter for a new line.
                </p>
              </div>
            </div>
            <div className="flex justify-end border-t border-slate-100 bg-slate-50/80 px-5 py-4">
              <button
                type="submit"
                disabled={isPending}
                className="inline-flex min-w-[148px] items-center justify-center gap-2 rounded-2xl bg-slate-950 px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    Search
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </div>
          </motion.form>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.3 }}
            className="mt-4 flex flex-col gap-2 sm:flex-row"
          >
            <Link
              href={query.trim() ? `/ai?q=${encodeURIComponent(query.trim())}` : "/ai"}
              className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-fuchsia-300 hover:text-slate-950"
            >
              <Sparkles className="h-4 w-4 text-fuchsia-600" />
              Open Buying Assistant
            </Link>
            <Link
              href="/compare"
              className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-orange-300 hover:text-slate-950"
            >
              Start Comparison
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.45 }}
            className="mt-8 flex flex-wrap items-center gap-6 text-sm text-slate-500"
          >
            {["Clear comparisons", "Transparent affiliate disclosure", "Growing product catalog"].map((item) => (
              <span key={item} className="inline-flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-fuchsia-500" aria-hidden="true" />
                {item}
              </span>
            ))}
          </motion.div>
        </div>

        <motion.aside
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.18 }}
          className="rounded-[2rem] border border-slate-200 bg-white/90 p-6 shadow-[0_24px_80px_-36px_rgba(15,23,42,0.28)] backdrop-blur"
        >
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Start here</p>
          <div className="mt-4 space-y-4">
            {[
              {
                title: "Compare two products side by side",
                description: "Open a structured comparison and focus on the trade-offs that actually matter.",
                href: "/compare?first=iphone16pro&second=galaxy-s25",
                label: "Open comparison",
              },
              {
                title: "Browse curated buying guides",
                description: "Read editorial guidance before spending time on scattered reviews.",
                href: "/guides",
                label: "See guides",
              },
              {
                title: "Get tailored help when the shortlist is messy",
                description: "Use the Buying Assistant when you need help balancing budget, priorities, and edge cases.",
                href: "/ai",
                label: "Open assistant",
              },
            ].map((item) => (
              <Link
                key={item.title}
                href={item.href}
                className="group block rounded-[1.5rem] border border-slate-200 bg-slate-50/70 p-5 transition hover:border-slate-300 hover:bg-white hover:shadow-md"
              >
                <h2 className="text-lg font-bold tracking-tight text-slate-950">{item.title}</h2>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{item.description}</p>
                <span className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-violet-700 transition group-hover:text-fuchsia-700">
                  {item.label}
                  <ArrowRight className="h-4 w-4" />
                </span>
              </Link>
            ))}
          </div>
        </motion.aside>
      </div>
    </section>
  );
}
