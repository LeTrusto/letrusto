import Link from "next/link";

import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { HomeTrendingSearch } from "@/config/homepage";

type HomeTrendingSearchesSectionProps = {
  title: string;
  subtitle?: string;
  items: HomeTrendingSearch[];
};

export default function HomeTrendingSearchesSection({
  title,
  subtitle,
  items,
}: HomeTrendingSearchesSectionProps) {
  return (
    <section className="mx-auto mt-18 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <Link
            key={item.label}
            href={item.href}
            className="group flex items-start justify-between gap-4 rounded-[1.5rem] border border-slate-200 bg-white p-5 shadow-sm transition duration-300 hover:-translate-y-0.5 hover:border-sky-200 hover:shadow-lg"
          >
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{item.note}</p>
              <h3 className="mt-2 text-lg font-bold text-slate-950 transition group-hover:text-sky-700">
                {item.label}
              </h3>
            </div>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-700 transition group-hover:bg-sky-50 group-hover:text-sky-700">
              Open
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}