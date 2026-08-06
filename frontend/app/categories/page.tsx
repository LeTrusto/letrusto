import type { Metadata } from "next";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import CategoryArtwork from "@/components/homepage/CategoryArtwork";
import { CATALOG_TREE } from "@/constants/index";

export const metadata: Metadata = {
  title: "Categories",
  description: "Browse all LeTrusto product categories and jump directly to comparisons and recommendations.",
  alternates: {
    canonical: "/categories",
  },
};

export default function CategoriesPage() {
  const allCategories = CATALOG_TREE.flatMap((group) => {
    if (!group.children || group.children.length === 0) {
      return [{ name: group.name, slug: group.slug, icon: group.icon, parent: group.name }];
    }

    return group.children.map((child) => ({ ...child, parent: group.name }));
  });

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(125,211,252,0.12),_transparent_24%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)]">
      <section className="mx-auto max-w-7xl px-6 py-14 md:py-18">
        <div className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">Browse the catalog</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950 md:text-6xl">Categories built for faster decisions</h1>
          <p className="mt-4 text-base leading-relaxed text-slate-600 md:text-lg">
            Explore product and service categories with a consistent decision-first experience across comparisons, recommendations, and research content.
          </p>
        </div>

        <div className="mt-8 grid gap-4 rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-3">
          {[
            { title: "Clear entry points", copy: "Start by category, brand, or search intent instead of navigating scattered product pages." },
            { title: "Consistent evaluation", copy: "Each category is designed to support comparison, context, and practical buying trade-offs." },
            { title: "Expanding coverage", copy: "Electronics is live now, with more categories being added using the same trust and editorial standards." },
          ].map((item) => (
            <article key={item.title} className="rounded-[1.5rem] bg-slate-50 p-5">
              <h2 className="text-lg font-bold text-slate-950">{item.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{item.copy}</p>
            </article>
          ))}
        </div>

        <div className="mt-10 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
        {allCategories.map((category) => (
          <Link
            key={category.slug}
            href={`/category/${category.slug}`}
            className="group h-full rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-violet-200 hover:shadow-[0_24px_80px_-32px_rgba(15,23,42,0.25)]"
          >
            <div className="flex h-full flex-col">
            <div className="flex items-center justify-between gap-3">
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                {category.parent}
              </span>
              <span className="inline-flex h-7 min-w-7 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 px-1.5 text-[11px] text-slate-500">
                {category.icon}
              </span>
            </div>
            <CategoryArtwork id={category.slug} className="mt-4" />
            <h2 className="mt-5 text-2xl font-black tracking-tight text-slate-950 group-hover:text-violet-700">{category.name}</h2>
            <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-600">
              Browse recommendations, compare top options, and explore buying guidance for this category.
            </p>
            <span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-slate-900 transition group-hover:text-violet-700">
              Explore category
              <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
            </span>
            </div>
          </Link>
        ))}
        </div>
      </section>
    </main>
  );
}
