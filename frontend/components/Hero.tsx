"use client";

import { motion } from "framer-motion";
import { ArrowRight, Loader2, Search, Sparkles } from "lucide-react";
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
      router.push(trimmed ? `/ai?q=${encodeURIComponent(trimmed)}` : "/ai");
    });
  }

  const chips = [
    "Best AI assistant for research",
    "AI writing tool for SEO",
    "AI coding assistant for startups",
    "AI video tool for creators",
  ];

  return (
    <section className="relative overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(168,85,247,0.16),_transparent_30%),radial-gradient(circle_at_85%_0%,_rgba(251,113,133,0.14),_transparent_28%),linear-gradient(180deg,#ffffff_0%,#fff7ed_100%)] py-18 md:py-22">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent" />
      <div className="pointer-events-none absolute -top-24 left-1/2 h-[440px] w-[440px] -translate-x-1/2 rounded-full bg-fuchsia-200/25 blur-3xl" />
      <div className="pointer-events-none absolute top-10 right-0 h-72 w-72 rounded-full bg-orange-100/40 blur-3xl" />
      <div className="pointer-events-none absolute -left-10 top-24 h-56 w-56 rounded-full bg-pink-100/30 blur-3xl" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="-mx-2 mb-4 flex snap-x gap-2 overflow-x-auto px-2 pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
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
                    router.push(`/ai?q=${encodeURIComponent(chip)}`);
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
            AI tools and software buying advisor
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.08 }}
            className="text-4xl font-black tracking-tight text-slate-950 md:text-6xl"
          >
            Find the right AI tool{" "}
            <span className="bg-gradient-to-r from-purple-600 via-pink-500 to-orange-500 bg-clip-text text-transparent">
              before you pay
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.16 }}
            className="mt-4 max-w-2xl text-lg leading-relaxed text-slate-600 md:text-[1.15rem]"
          >
            LeTrusto helps teams and creators compare AI tools, understand software trade-offs, and choose confidently before subscription spend.
          </motion.p>

          <motion.form
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.24 }}
            onSubmit={handleSearch}
            className="mt-7 rounded-[1.7rem] bg-gradient-to-r from-purple-200/70 via-pink-200/70 to-orange-200/70 p-[1.2px] shadow-[0_22px_64px_-32px_rgba(15,23,42,0.32)] transition duration-300 focus-within:-translate-y-0.5 focus-within:shadow-[0_28px_80px_-36px_rgba(139,92,246,0.34)]"
          >
            <div className="overflow-hidden rounded-[calc(1.7rem-1.2px)] border border-white/80 bg-white/95 backdrop-blur">
              <div className="flex flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:gap-4 sm:px-5 sm:py-4 md:px-6">
                <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-fuchsia-100 to-orange-100 text-fuchsia-700 transition-colors duration-300 sm:mt-0">
                  <Search className="h-5 w-5" aria-hidden="true" />
                </div>
                <div className="flex-1">
                  <label htmlFor="hero-search" className="sr-only">Ask LeTrusto about AI tools</label>
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
                      target.style.height = `${Math.min(target.scrollHeight, 136)}px`;
                    }}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" && !event.shiftKey) {
                        event.preventDefault();
                        event.currentTarget.form?.requestSubmit();
                      }
                    }}
                    aria-describedby="hero-search-hint"
                    placeholder="Ask LeTrusto which AI tool fits your workflow, budget, or team size."
                    className="min-h-[56px] w-full resize-none bg-transparent py-[14px] text-[18px] leading-7 text-slate-900 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-70"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isPending}
                  className="inline-flex min-w-[148px] items-center justify-center gap-2 self-end rounded-2xl bg-slate-950 px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 sm:self-center"
                >
                  {isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      Ask LeTrusto
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </motion.form>

          <p id="hero-search-hint" className="mt-2 text-sm text-slate-500">
            Press Enter to search. Use Shift+Enter for a new line.
          </p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.45 }}
            className="mt-6 flex flex-wrap items-center gap-6 text-sm text-slate-500"
          >
            {["AI tool comparisons", "Transparent affiliate disclosure", "Research-first recommendations"].map((item) => (
              <span key={item} className="inline-flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-fuchsia-500" aria-hidden="true" />
                {item}
              </span>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
