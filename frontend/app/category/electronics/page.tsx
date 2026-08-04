import type { Metadata } from "next";
import Link from "next/link";

import ProductCard from "@/components/ProductCard";
import { getAllProducts, type Product } from "@/services/product.service";

export const metadata: Metadata = {
  title: "Electronics | LeTrusto",
  description: "AI-first electronics buying workspace with guided discovery, comparisons, and practical recommendations.",
};

const ELECTRONICS_CATEGORIES = new Set([
  "phone",
  "smartphones",
  "laptop",
  "headphones",
  "smartwatch",
  "camera",
  "gaming",
  "television",
  "tablet",
  "earbuds-tws",
  "bluetooth-speakers",
  "monitors-displays",
]);

const FEATURED_COMPARISONS = [
  {
    title: "iPhone 16 Pro vs Galaxy S25",
    description: "Camera consistency, software lifecycle, and resale value.",
    href: "/compare?first=iphone16pro&second=galaxy-s25",
  },
  {
    title: "MacBook Air M4 vs ZenBook 14 OLED",
    description: "Battery, build, and long-term performance for developers.",
    href: "/compare?first=macbook-air-m4&second=asus-zenbook-14-oled",
  },
  {
    title: "Sony WH-1000XM6 vs Bose QC Ultra",
    description: "ANC quality, comfort, and multi-device workflows.",
    href: "/compare?first=sony-wh-1000xm6&second=bose-qc-ultra",
  },
];

const BUYING_GUIDES = [
  {
    title: "Best Phone Under 30000",
    excerpt: "A practical framework to choose camera, battery, and performance priorities.",
    href: "/articles/best-phone-under-20000-india-2026",
  },
  {
    title: "Gaming Laptop Checklist",
    excerpt: "How to prioritize GPU power, thermal design, and display quality.",
    href: "/guides",
  },
  {
    title: "TV Buying Guide for 2026",
    excerpt: "Understand panel technologies and pick right screen size for your room.",
    href: "/guides",
  },
];

function parseSearchParam(value?: string | string[]) {
  if (!value) return "";
  return Array.isArray(value) ? value[0] : value;
}

function filterElectronics(
  products: Product[],
  searchQuery: string,
  selectedCategory: string,
  minAiScore: number
) {
  return products.filter((product) => {
    const isElectronics = ELECTRONICS_CATEGORIES.has(String(product.category));
    if (!isElectronics) return false;

    if (selectedCategory !== "all" && String(product.category) !== selectedCategory) {
      return false;
    }

    if (product.aiScore < minAiScore) {
      return false;
    }

    if (!searchQuery) {
      return true;
    }

    const haystack = `${product.name} ${product.brand} ${product.category} ${product.tags.join(" ")}`.toLowerCase();
    return haystack.includes(searchQuery.toLowerCase());
  });
}

export default async function ElectronicsCategoryPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string | string[]; sub?: string | string[]; minAi?: string | string[] }>;
}) {
  const params = await searchParams;
  const allProducts = await getAllProducts();

  const q = parseSearchParam(params.q);
  const sub = parseSearchParam(params.sub) || "all";
  const minAiRaw = Number(parseSearchParam(params.minAi) || "0");
  const minAi = Number.isFinite(minAiRaw) && minAiRaw > 0 ? minAiRaw : 0;

  const electronicsProducts = filterElectronics(allProducts, q, sub, minAi).sort((a, b) => b.aiScore - a.aiScore);

  return (
    <main className="min-h-screen bg-slate-50 pb-14">
      <section className="relative overflow-hidden bg-[radial-gradient(circle_at_top_right,_#dbeafe,_transparent_55%),radial-gradient(circle_at_bottom_left,_#e9d5ff,_transparent_40%),linear-gradient(135deg,#0f172a,#312e81,#0f172a)] py-18 text-white">
        <div className="mx-auto max-w-7xl px-6">
          <p className="inline-flex rounded-full border border-white/30 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em]">
            AI Buying Workspace
          </p>
          <h1 className="mt-4 max-w-3xl text-4xl font-black tracking-tight md:text-6xl">Electronics, guided by intelligence not guesswork.</h1>
          <p className="mt-4 max-w-2xl text-white/85 md:text-lg">
            LeTrusto helps you discover, compare, and choose electronics with AI-backed recommendations and practical trust signals.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link href="/ai" className="rounded-xl bg-white px-5 py-3 text-sm font-bold text-indigo-700">
              Ask AI Advisor
            </Link>
            <Link href="/compare" className="rounded-xl border border-white/40 px-5 py-3 text-sm font-semibold text-white">
              Open Comparison Lab
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto -mt-8 max-w-7xl px-6">
        <form className="grid gap-4 rounded-3xl border border-slate-200 bg-white p-5 shadow-lg md:grid-cols-4" method="get">
          <label className="text-sm font-semibold text-slate-700">
            Search
            <input
              name="q"
              defaultValue={q}
              placeholder="iphone, creator laptop, ANC headphones"
              className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-violet-400"
            />
          </label>

          <label className="text-sm font-semibold text-slate-700">
            Category
            <select name="sub" defaultValue={sub} className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-violet-400">
              <option value="all">All electronics</option>
              <option value="phone">Phones</option>
              <option value="laptop">Laptops</option>
              <option value="headphones">Headphones</option>
              <option value="smartwatch">Smartwatches</option>
              <option value="camera">Cameras</option>
              <option value="gaming">Gaming</option>
              <option value="television">TVs</option>
              <option value="tablet">Tablets</option>
            </select>
          </label>

          <label className="text-sm font-semibold text-slate-700">
            Min AI Score
            <select name="minAi" defaultValue={String(minAi)} className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-violet-400">
              <option value="0">Any score</option>
              <option value="85">85+</option>
              <option value="90">90+</option>
              <option value="94">94+</option>
            </select>
          </label>

          <div className="flex items-end gap-2">
            <button type="submit" className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-2.5 text-sm font-bold text-white">
              Apply
            </button>
            <Link href="/category/electronics" className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700">
              Reset
            </Link>
          </div>
        </form>
      </section>

      <section className="mx-auto mt-10 max-w-7xl px-6">
        <h2 className="text-2xl font-black tracking-tight text-slate-900">Featured Comparisons</h2>
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          {FEATURED_COMPARISONS.map((item) => (
            <Link key={item.title} href={item.href} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
              <h3 className="text-lg font-bold text-slate-900">{item.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{item.description}</p>
              <span className="mt-3 inline-flex text-sm font-semibold text-violet-700">Open comparison</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="mx-auto mt-10 max-w-7xl px-6">
        <h2 className="text-2xl font-black tracking-tight text-slate-900">Buying Guides</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {BUYING_GUIDES.map((guide) => (
            <Link key={guide.title} href={guide.href} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
              <p className="text-xs font-semibold uppercase tracking-wide text-violet-600">Guide</p>
              <h3 className="mt-2 text-lg font-bold text-slate-900">{guide.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{guide.excerpt}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className="mx-auto mt-12 max-w-7xl px-6">
        <div className="mb-6 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-3xl font-black tracking-tight text-slate-900">AI Ranked Products</h2>
            <p className="mt-1 text-sm text-slate-500">{electronicsProducts.length} electronics matched your filters.</p>
          </div>
        </div>

        {electronicsProducts.length > 0 ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {electronicsProducts.map((product) => (
              <ProductCard key={product.id} product={product} highlightLabel="AI Ranked" aiReason={product.aiSummary} />
            ))}
          </div>
        ) : (
          <div className="rounded-3xl border border-slate-200 bg-white p-8 text-center">
            <h3 className="text-xl font-bold text-slate-900">No electronics matched these filters.</h3>
            <p className="mt-2 text-sm text-slate-600">Try broadening category or AI score filters.</p>
          </div>
        )}
      </section>
    </main>
  );
}
