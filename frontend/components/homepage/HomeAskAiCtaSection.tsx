import Link from "next/link";
import { Sparkles } from "lucide-react";

type HomeAskAiCtaSectionProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
};

export default function HomeAskAiCtaSection({
  title,
  subtitle,
  ctaLabel,
  ctaHref,
}: HomeAskAiCtaSectionProps) {
  return (
    <section className="mx-auto mt-20 w-full max-w-7xl px-6 pb-20">
      <div className="relative overflow-hidden rounded-3xl border border-violet-200 bg-gradient-to-br from-violet-600 via-fuchsia-600 to-indigo-700 p-8 text-white shadow-xl md:p-12">
        <div className="absolute -top-24 -right-16 h-56 w-56 rounded-full bg-white/15 blur-3xl" aria-hidden="true" />
        <div className="absolute -bottom-24 -left-12 h-56 w-56 rounded-full bg-black/15 blur-3xl" aria-hidden="true" />

        <div className="relative z-10 max-w-3xl">
          <p className="inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-wide">
            <Sparkles className="h-3.5 w-3.5" />
            AI Buying Advisor
          </p>
          <h2 className="mt-4 text-3xl font-black tracking-tight md:text-5xl">{title}</h2>
          {subtitle ? <p className="mt-3 text-white/90 md:text-lg">{subtitle}</p> : null}
          {ctaLabel && ctaHref ? (
            <Link
              href={ctaHref}
              className="mt-7 inline-flex items-center justify-center rounded-xl bg-white px-6 py-3 text-sm font-bold text-violet-700 transition hover:bg-violet-50"
            >
              {ctaLabel}
            </Link>
          ) : null}
        </div>
      </div>
    </section>
  );
}
