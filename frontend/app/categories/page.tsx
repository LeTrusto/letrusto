import type { Metadata } from "next";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import CategoryArtwork from "@/components/homepage/CategoryArtwork";
import SchemaOrg from "@/components/SchemaOrg";
import { AI_TOOLS_PUBLIC_CATEGORIES } from "@/config/aiTools";

export const metadata: Metadata = {
  title: "AI Tools",
  description: "Explore AI tool categories and find the right software before you pay.",
  alternates: {
    canonical: "/categories",
  },
  openGraph: {
    title: "AI Tools",
    description: "Explore AI tool categories and find the right software before you pay.",
    url: "/categories",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Tools",
    description: "Explore AI tool categories and find the right software before you pay.",
    images: ["/images/og-default.svg"],
  },
};

export default function CategoriesPage() {
  const allCategories = AI_TOOLS_PUBLIC_CATEGORIES;

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(125,211,252,0.12),_transparent_24%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)]">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "AI Tools",
          url: "https://letrusto.com/categories",
          description: "Explore AI tool categories and find the right software before you pay.",
        }}
      />
      <section className="mx-auto max-w-7xl px-6 py-14 md:py-18">
        <div className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">AI Tools</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950 md:text-6xl">Find the right AI tool for your needs</h1>
          <p className="mt-4 text-base leading-relaxed text-slate-600 md:text-lg">
            Start with the right category, compare options clearly, and make software buying decisions with confidence.
          </p>
        </div>

        <div className="mt-8 grid gap-4 rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-3">
          {[
            { title: "Decision-first", copy: "Each category is structured to help evaluate value, fit, and trade-offs before subscription spend." },
            { title: "No fake listings", copy: "Categories can be ready for content even when we are still curating trusted tool coverage." },
            { title: "Future expansion", copy: "SaaS and hosting are on our roadmap, while AI tools remain the primary focus." },
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
            key={category.id}
            href={category.href}
            className="group h-full rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-violet-200 hover:shadow-[0_24px_80px_-32px_rgba(15,23,42,0.25)]"
          >
            <div className="flex h-full flex-col">
            <div className="flex items-center justify-between gap-3">
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                Category
              </span>
              <span className="inline-flex h-7 min-w-7 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 px-1.5 text-[11px] text-slate-500">
                {category.icon}
              </span>
            </div>
            <CategoryArtwork id={category.id} className="mt-4" />
            <h2 className="mt-5 text-2xl font-black tracking-tight text-slate-950 group-hover:text-violet-700">{category.name}</h2>
            <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-600">
              {category.description}
            </p>
            <span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-slate-900 transition group-hover:text-violet-700">
              Open category
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
