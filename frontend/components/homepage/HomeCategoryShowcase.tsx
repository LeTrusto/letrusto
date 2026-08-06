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
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <Link
            key={item.id}
            href={item.href}
            className="group relative isolate h-full overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm transition duration-500 ease-out hover:-translate-y-1 hover:border-violet-200 hover:shadow-[0_24px_80px_-32px_rgba(15,23,42,0.28)]"
            aria-label={`Browse ${item.name}`}
          >
            <div className="relative flex min-h-[350px] flex-col">
              <div className="flex items-center justify-between gap-3">
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  {item.eyebrow}
                </span>
                <span className="rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700">
                  {item.productCountText}
                </span>
              </div>

              <CategoryArtwork id={item.id} className="mt-4" />

              <div className="mt-5 flex-1">
                <h3 className="text-2xl font-black tracking-tight text-slate-950 md:text-[1.85rem]">{item.name}</h3>
                <p className="mt-2.5 max-w-md text-sm leading-relaxed text-slate-600 md:text-base">{item.description}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {item.featuredBullets.map((bullet) => (
                    <span
                      key={`${item.id}-${bullet}`}
                      className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600"
                    >
                      {bullet}
                    </span>
                  ))}
                </div>
              </div>

              <span className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-900 transition duration-300 group-hover:translate-x-0.5 group-hover:text-violet-700">
                {item.productCount === 0 ? "Preview roadmap" : "Explore category"}
                <ArrowUpRight className="h-4 w-4" />
              </span>
              <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent" aria-hidden="true" />
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
