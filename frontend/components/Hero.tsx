"use client";

import { motion } from "framer-motion";

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-white to-gray-50 py-24 text-center">
      <div className="pointer-events-none absolute -top-24 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-fuchsia-300/20 blur-3xl" />

      <motion.h1
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mx-auto max-w-5xl text-5xl font-black tracking-tight text-gray-900 md:text-7xl"
      >
        Know Before You Buy.
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, delay: 0.1 }}
        className="mx-auto mt-6 max-w-3xl text-xl text-gray-600"
      >
        AI-powered shopping assistant that compares products, analyzes reviews,
        tracks prices, and helps you make confident buying decisions.
      </motion.p>
    </section>
  );
}
