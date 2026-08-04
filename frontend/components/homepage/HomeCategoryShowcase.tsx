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
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <Link
            key={item.id}
            href={item.href}
            className="group relative isolate overflow-hidden rounded-[2rem] border border-slate-200/80 bg-slate-900 p-7 text-white shadow-sm transition duration-500 ease-out hover:-translate-y-1.5 hover:shadow-2xl hover:shadow-slate-900/30"
            aria-label={`Browse ${item.name}`}
          >
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(255,255,255,0.15),transparent_35%),radial-gradient(circle_at_85%_15%,rgba(255,255,255,0.12),transparent_30%)]" aria-hidden="true" />
            <div
              className="absolute inset-0 bg-cover bg-center opacity-75 transition duration-700 ease-out group-hover:scale-110"
              style={{ backgroundImage: `url(${item.image})` }}
              aria-hidden="true"
            />
            <div
              className={`absolute inset-0 bg-gradient-to-br ${item.gradientClass} mix-blend-multiply transition duration-500 group-hover:opacity-95`}
              aria-hidden="true"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-900/50 to-transparent" aria-hidden="true" />
            <div className="absolute inset-0 rounded-[2rem] ring-1 ring-white/15" aria-hidden="true" />

            <div className="relative z-10 flex min-h-[250px] flex-col justify-between">
              <div className="flex flex-wrap gap-2">
                <div className="inline-flex w-fit rounded-full border border-white/30 bg-white/15 px-3 py-1 text-xs font-semibold tracking-wide backdrop-blur-md">
                  {item.productCountText}
                </div>
                {item.productCount === 0 ? (
                  <div className="inline-flex w-fit rounded-full border border-white/30 bg-black/25 px-3 py-1 text-xs font-semibold tracking-wide backdrop-blur-md">
                    Coming Soon
                  </div>
                ) : null}
              </div>
              <div>
                <h3 className="text-3xl font-black tracking-tight leading-tight md:text-[2rem]">{item.name}</h3>
                <p className="mt-2.5 max-w-sm text-sm leading-relaxed text-slate-100/90 md:text-base">{item.description}</p>
                <span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-white/95 transition duration-300 group-hover:translate-x-0.5">
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
