import Link from "next/link";

import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { HomeFeaturedBrand } from "@/config/homepage";

type HomeFeaturedBrandsSectionProps = {
  title: string;
  subtitle?: string;
  items: HomeFeaturedBrand[];
};

export default function HomeFeaturedBrandsSection({
  title,
  subtitle,
  items,
}: HomeFeaturedBrandsSectionProps) {
  return (
    <section className="mx-auto mt-18 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {items.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className="group rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm transition duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-lg"
          >
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{item.category}</p>
            <h3 className="mt-3 text-2xl font-black tracking-tight text-slate-950 transition group-hover:text-sky-700">
              {item.name}
            </h3>
            <p className="mt-2 text-sm text-slate-600">{item.note}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}