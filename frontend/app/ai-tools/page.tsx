import type { Metadata } from "next";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import CategoryArtwork from "@/components/homepage/CategoryArtwork";
import SchemaOrg from "@/components/SchemaOrg";
import { AI_TOOLS_PUBLIC_CATEGORIES } from "@/config/aiTools";
import { getAiTools } from "@/services/ai-tools.service";

export const metadata: Metadata = {
  title: "AI Tools",
  description: "Find the right AI tool for your needs.",
  alternates: {
    canonical: "/ai-tools",
  },
  openGraph: {
    title: "AI Tools",
    description: "Find the right AI tool for your needs.",
    url: "/ai-tools",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Tools",
    description: "Find the right AI tool for your needs.",
    images: ["/images/og-default.svg"],
  },
};

export default async function AIToolsPage() {
  const tools = await getAiTools();

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(125,211,252,0.12),_transparent_24%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)]">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "AI Tools",
          url: "https://letrusto.com/ai-tools",
          description: "Find the right AI tool for your needs.",
        }}
      />

      <section className="mx-auto max-w-7xl px-6 py-14 md:py-18">
        <div className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">AI Tools</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950 md:text-6xl">Find the right AI tool for your needs</h1>
          <p className="mt-4 text-base leading-relaxed text-slate-600 md:text-lg">
            Explore AI tool categories built for practical software buying decisions, clear comparisons, and trusted guidance.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/ai" className="rounded-xl bg-slate-950 px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-800">
              Ask LeTrusto
            </Link>
            <Link href="/compare" className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-500 hover:text-slate-900">
              Compare options
            </Link>
          </div>
        </div>

        <div className="mt-10 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {AI_TOOLS_PUBLIC_CATEGORIES.map((category) => (
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
                <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-600">{category.description}</p>
                <span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-slate-900 transition group-hover:text-violet-700">
                  Open category
                  <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
                </span>
              </div>
            </Link>
          ))}
        </div>

        <section className="mt-14">
          <div className="mb-6 flex items-end justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Published Tools</p>
              <h2 className="mt-2 text-3xl font-black tracking-tight text-slate-950">Verified AI Tool Profiles</h2>
            </div>
            <span className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600">
              {tools.items.length} published
            </span>
          </div>

          {tools.items.length === 0 ? (
            <div className="rounded-3xl border border-slate-200 bg-white p-8 text-slate-600 shadow-sm">
              No published tools are available yet.
            </div>
          ) : (
            <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {tools.items.map((tool) => (
                <Link
                  key={tool.slug}
                  href={`/ai-tools/${tool.slug}`}
                  className="group rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:border-sky-200"
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{tool.category.name}</p>
                  <h3 className="mt-2 text-2xl font-black tracking-tight text-slate-950 group-hover:text-sky-700">{tool.name}</h3>
                  <p className="mt-1 text-sm font-semibold text-slate-600">{tool.provider}</p>
                  <p className="mt-3 text-sm leading-relaxed text-slate-600">{tool.description}</p>
                  <span className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-slate-900 group-hover:text-sky-700">
                    Open profile
                    <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
                  </span>
                </Link>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
