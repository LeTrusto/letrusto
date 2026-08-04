import Link from "next/link";
import { BellRing, Rocket, Sparkles } from "lucide-react";

import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";

export type ComingSoonVertical = {
  id: string;
  title: string;
  subtitle: string;
  illustration: string;
  eta: string;
  route: string;
  planned: string[];
};

type HomeComingSoonRoadmapSectionProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
  items: ComingSoonVertical[];
};

export default function HomeComingSoonRoadmapSection({
  title,
  subtitle,
  ctaLabel,
  ctaHref,
  items,
}: HomeComingSoonRoadmapSectionProps) {
  return (
    <section className="mx-auto mt-16 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} ctaLabel={ctaLabel} ctaHref={ctaHref} />
      <div className="grid gap-5 lg:grid-cols-2">
        {items.map((item) => (
          <article
            key={item.id}
            className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
          >
            <div className="absolute -top-16 -right-16 h-36 w-36 rounded-full bg-sky-100 blur-2xl" aria-hidden="true" />
            <div className="absolute -bottom-16 -left-16 h-36 w-36 rounded-full bg-violet-100 blur-2xl" aria-hidden="true" />

            <div className="relative z-10">
              <p className="text-4xl" aria-hidden="true">{item.illustration}</p>
              <h3 className="mt-3 text-2xl font-black tracking-tight text-slate-900">{item.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{item.subtitle}</p>

              <p className="mt-4 inline-flex items-center gap-2 rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">
                <Rocket className="h-3.5 w-3.5" />
                Launch target: {item.eta}
              </p>

              <div className="mt-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Planned in roadmap</p>
                <ul className="mt-2 space-y-1.5 text-sm text-slate-700">
                  {item.planned.map((entry) => (
                    <li key={`${item.id}-${entry}`} className="flex items-start gap-2">
                      <Sparkles className="mt-0.5 h-3.5 w-3.5 shrink-0 text-violet-500" />
                      <span>{entry}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-5 flex flex-wrap gap-3">
                <Link
                  href={item.route}
                  className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:text-slate-900"
                >
                  View roadmap
                </Link>
                <Link
                  href={`/support?tab=contact&category=feedback`}
                  className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-2 text-sm font-bold text-white"
                >
                  <BellRing className="h-4 w-4" />
                  Notify Me
                </Link>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
