import Link from "next/link";
import { Sparkles } from "lucide-react";

export default function HomeAskLetrustoSection() {
  return (
    <section className="mx-auto max-w-7xl px-6 py-14">
      <div className="rounded-[var(--radius-2xl)] bg-gradient-to-br from-slate-900 via-[var(--lt-purple-dark)] to-slate-900 px-8 py-12 text-center md:px-16 md:py-16">
        <Sparkles className="mx-auto h-8 w-8 text-[var(--lt-purple-light)]" />
        <h2 className="mt-4 text-2xl font-black tracking-tight text-white md:text-3xl">
          Not sure which AI tool is right for you?
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-base leading-relaxed text-slate-300">
          Tell LeTrusto what you&apos;re trying to accomplish and get a practical starting point — no sign-up required.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link href="/ai" className="lt-btn lt-btn-lg lt-btn-brand">
            <Sparkles className="h-4 w-4" /> Ask LeTrusto
          </Link>
          <Link href="/ai-tools" className="lt-btn lt-btn-lg border-white/20 text-white hover:bg-white/10">
            Explore AI Tools
          </Link>
        </div>
      </div>
    </section>
  );
}
