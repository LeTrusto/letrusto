import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import CategoryArtwork from "@/components/homepage/CategoryArtwork";
import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { HomeCategoryCard } from "@/services/homepage.service";

type HomeCategoryShowcaseProps = {
  title: string;
  subtitle?: string;
  items: HomeCategoryCard[];
};

export default function HomeCategoryShowcase({
  title,
  subtitle,
  items,
}: HomeCategoryShowcaseProps) {
  return (
    <section className="mx-auto mt-14 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {items.map((item) => (
          <Link
            key={item.id}
            href={item.href}
            className="group relative isolate overflow-hidden rounded-[1.5rem] border border-slate-200 bg-white p-3.5 shadow-sm transition duration-500 ease-out hover:-translate-y-0.5 hover:border-violet-200 hover:shadow-[0_20px_56px_-30px_rgba(15,23,42,0.34)]"
            aria-label={`Browse ${item.name}`}
          >
            <div className="relative flex min-h-[212px] flex-col">
              <div className="flex items-center justify-between gap-3">
                <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">
                  {item.eyebrow}
                </span>
                <span className="rounded-full bg-sky-50 px-2.5 py-0.5 text-[10px] font-semibold text-sky-700">
                  {item.productCountText}
                </span>
              </div>

              <CategoryArtwork id={item.id} className="mt-3" />

              <div className="mt-3.5 flex-1">
                <h3 className="text-base font-black tracking-tight text-slate-950">{item.name}</h3>
                <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-600">{item.description}</p>
              </div>

              <span className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-slate-900 transition duration-300 group-hover:translate-x-0.5 group-hover:text-violet-700">
                {item.productCount === 0 ? "Preview roadmap" : "Explore category"}
                <ArrowUpRight className="h-3.5 w-3.5" />
              </span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
