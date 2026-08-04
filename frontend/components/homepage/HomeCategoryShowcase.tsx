import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

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
            className="group relative overflow-hidden rounded-3xl border border-slate-200 bg-slate-900 p-6 text-white transition duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-slate-900/25"
            aria-label={`Browse ${item.name}`}
          >
            <div
              className="absolute inset-0 bg-cover bg-center opacity-70 transition duration-500 group-hover:scale-105"
              style={{ backgroundImage: `url(${item.image})` }}
              aria-hidden="true"
            />
            <div
              className={`absolute inset-0 bg-gradient-to-br ${item.gradientClass} mix-blend-multiply`}
              aria-hidden="true"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/85 via-slate-900/40 to-transparent" aria-hidden="true" />

            <div className="relative z-10 flex min-h-[220px] flex-col justify-between">
              <div className="flex flex-wrap gap-2">
                <div className="inline-flex w-fit rounded-full border border-white/25 bg-white/10 px-3 py-1 text-xs font-semibold backdrop-blur">
                  {item.productCountText}
                </div>
                {item.productCount === 0 ? (
                  <div className="inline-flex w-fit rounded-full border border-white/25 bg-black/20 px-3 py-1 text-xs font-semibold backdrop-blur">
                    Coming Soon
                  </div>
                ) : null}
              </div>
              <div>
                <h3 className="text-2xl font-bold tracking-tight">{item.name}</h3>
                <p className="mt-2 max-w-sm text-sm text-slate-100/90">{item.description}</p>
                <span className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-white/95">
                  {item.productCount === 0 ? "View roadmap" : "Explore category"}
                  <ArrowUpRight className="h-4 w-4" />
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
