"use client";

import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Hero() {
  const [query, setQuery] = useState("");
  const router = useRouter();

  function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) {
      router.push("/ai");
    } else {
      router.push(`/ai?q=${encodeURIComponent(query.trim())}`);
    }
  }

  const chips = [
    "Best phone under ₹30,000",
    "Laptop for coding",
    "Gaming console 2026",
    "Best web hosting India",
  ];

  return (
    <section className="relative overflow-hidden bg-white py-20 text-center">
      {/* Ambient glow */}
      <div className="pointer-events-none absolute -top-32 left-1/2 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-purple-200/25 blur-3xl" />
      <div className="pointer-events-none absolute top-0 right-0 h-64 w-64 rounded-full bg-pink-200/20 blur-3xl" />
      <div className="pointer-events-none absolute top-10 left-0 h-48 w-48 rounded-full bg-orange-200/15 blur-3xl" />

      <div className="relative mx-auto max-w-4xl px-6">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mb-6 inline-flex items-center gap-2 rounded-full border border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50 px-4 py-2 text-sm font-semibold text-purple-700"
        >
          <Sparkles className="h-4 w-4 text-purple-500" />
          India&apos;s AI Buying Advisor
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
          className="text-5xl font-black tracking-tight text-gray-900 md:text-7xl"
        >
          Know Before{" "}
          <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-orange-500 bg-clip-text text-transparent">
            You Buy
          </span>
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.12 }}
          className="mx-auto mt-5 max-w-2xl text-lg text-gray-500 md:text-xl"
        >
          Tell our AI what you need. Get the smartest recommendation in seconds.
        </motion.p>

        {/* AI Prompt Box */}
        <motion.form
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          onSubmit={handleAsk}
          className="mx-auto mt-8 flex max-w-2xl gap-3 rounded-2xl border border-gray-200 bg-white p-2 shadow-lg shadow-purple-100/50"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Best phone under ₹30,000 with great camera..."
            className="flex-1 rounded-xl bg-transparent px-4 py-3 text-sm text-gray-800 placeholder-gray-400 outline-none"
          />
          <button
            type="submit"
            className="flex shrink-0 items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-5 py-3 text-sm font-bold text-white shadow-md transition hover:scale-[1.03]"
          >
            Ask AI
            <ArrowRight className="h-4 w-4" />
          </button>
        </motion.form>

        {/* Quick chips */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-4 flex flex-wrap justify-center gap-2"
        >
          {chips.map((chip) => (
            <button
              key={chip}
              type="button"
              onClick={() => router.push(`/ai?q=${encodeURIComponent(chip)}`)}
              className="rounded-full border border-gray-200 bg-white px-3 py-1.5 text-xs font-medium text-gray-600 transition hover:border-purple-300 hover:text-purple-700"
            >
              {chip}
            </button>
          ))}
        </motion.div>

        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.35 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-4"
        >
          <Link
            href="/ai"
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 px-6 py-3 text-sm font-bold text-white shadow-md transition hover:scale-[1.03]"
          >
            <Sparkles className="h-4 w-4" />
            Start AI Advisor
          </Link>
          <Link
            href="/search"
            className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-sm font-semibold text-gray-700 transition hover:border-purple-300 hover:text-purple-700"
          >
            Browse Products
            <ArrowRight className="h-4 w-4" />
          </Link>
        </motion.div>

        {/* Trust indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.45 }}
          className="mt-10 flex flex-wrap items-center justify-center gap-6 text-xs font-medium text-gray-400"
        >
          {["🤖 AI-powered", "📊 Unbiased reviews", "🔒 No spam", "421+ products"].map((item) => (
            <span key={item}>{item}</span>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
