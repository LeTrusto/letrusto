import Link from "next/link";

import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { HomepageComparisonItem } from "@/config/homepage";

type HomePopularComparisonsSectionProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
  items: HomepageComparisonItem[];
};

export default function HomePopularComparisonsSection({
  title,
  subtitle,
  ctaLabel,
  ctaHref,
  items,
}: HomePopularComparisonsSectionProps) {
  return (
    <section className="mx-auto mt-16 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} ctaLabel={ctaLabel} ctaHref={ctaHref} />

      <div className="grid gap-5 lg:grid-cols-3">
        {items.map((item) => (
          <Link
            key={item.id}
            href={item.href}
            className="group relative overflow-hidden rounded-[1.9rem] border border-slate-200 bg-white p-6 shadow-sm transition duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-xl"
          >
            <div className={`absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r ${item.accent}`} aria-hidden="true" />
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Popular Decision</p>
            <h3 className="mt-3 text-2xl font-black tracking-tight text-slate-900">{item.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-600">{item.subtitle}</p>
            <span className="mt-5 inline-flex text-sm font-semibold text-sky-700 transition group-hover:text-sky-900">
              Compare now
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
