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
  const chipStyles = [
    "from-sky-100 to-blue-100 border-sky-200/80 text-sky-800 hover:from-sky-200 hover:to-blue-200",
    "from-violet-100 to-purple-100 border-violet-200/80 text-violet-800 hover:from-violet-200 hover:to-purple-200",
    "from-orange-100 to-amber-100 border-orange-200/80 text-orange-800 hover:from-orange-200 hover:to-amber-200",
    "from-emerald-100 to-green-100 border-emerald-200/80 text-emerald-800 hover:from-emerald-200 hover:to-green-200",
    "from-pink-100 to-rose-100 border-pink-200/80 text-pink-800 hover:from-pink-200 hover:to-rose-200",
    "from-teal-100 to-cyan-100 border-teal-200/80 text-teal-800 hover:from-teal-200 hover:to-cyan-200",
  ];

  return (
    <section className="mx-auto mt-14 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} />
      <div className="flex flex-wrap gap-3">
        {items.map((item, index) => (
          <Link
            key={item.label}
            href={item.href}
            className={`group inline-flex items-center gap-2 rounded-full border bg-gradient-to-r px-4 py-2.5 text-sm font-semibold shadow-[0_8px_24px_-14px_rgba(15,23,42,0.45)] transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_14px_32px_-16px_rgba(15,23,42,0.45)] ${chipStyles[index % chipStyles.length]}`}
          >
            <span>{item.label}</span>
            <span className="rounded-full bg-white/70 px-2 py-0.5 text-[11px] font-bold uppercase tracking-[0.08em]">
              {item.note}
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}