import type { Metadata } from "next";
import Link from "next/link";

import ProductCard from "@/components/ProductCard";
import { getAllProducts, type Product } from "@/services/product.service";

export const metadata: Metadata = {
  title: "Electronics | LeTrusto",
  description: "AI-first electronics buying workspace with guided discovery, premium comparisons, and trusted recommendations.",
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

const SUBCATEGORY_CHIPS = [
  { label: "Phones", value: "phone" },
  { label: "Laptops", value: "laptop" },
  { label: "Gaming", value: "gaming" },
  { label: "TV", value: "television" },
  { label: "Camera", value: "camera" },
  { label: "Audio", value: "headphones" },
  { label: "Wearables", value: "smartwatch" },
  { label: "Accessories", value: "tablet" },
];

const FEATURED_COMPARISONS = [
  {
    title: "iPhone 16 Pro vs Galaxy S25",
    description: "Camera consistency, software lifecycle, and resale value.",
    href: "/compare?first=iphone16pro&second=galaxy-s25",
  },
  {
    title: "MacBook Air M4 vs ZenBook 14 OLED",
    description: "Battery endurance, build quality, and coding reliability.",
    href: "/compare?first=macbook-air-m4&second=asus-zenbook-14-oled",
  },
  {
    title: "WH-1000XM6 vs Bose QC Ultra",
    description: "Noise cancellation depth, comfort, and call quality.",
    href: "/compare?first=sony-wh-1000xm6&second=bose-qc-ultra",
  },
];

const BUYING_GUIDES = [
  {
    title: "Best Phone Under 30000",
    excerpt: "A framework for balancing camera, battery, software, and long-term value.",
    href: "/articles/best-phone-under-20000-india-2026",
  },
  {
    title: "Gaming Laptop Decision Guide",
    excerpt: "How to prioritize GPU class, thermals, display quality, and upgrade paths.",
    href: "/guides",
  },
  {
    title: "TV Setup and Buying Guide",
    excerpt: "Pick the right panel technology and screen size for your room and usage.",
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
    <main className="min-h-screen bg-slate-50 pb-20">
      <section className="relative overflow-hidden bg-[radial-gradient(circle_at_top_right,_#dbeafe,_transparent_50%),radial-gradient(circle_at_bottom_left,_#e9d5ff,_transparent_45%),linear-gradient(135deg,#0f172a,#312e81,#0f172a)] py-18 text-white md:py-24">
        <div className="mx-auto max-w-7xl px-6">
          <p className="inline-flex rounded-full border border-white/30 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em]">
            AI Buying Advisor
          </p>
          <h1 className="mt-4 max-w-4xl text-4xl font-black tracking-tight md:text-6xl">
            Electronics decisions, guided by intelligence not catalog noise.
          </h1>
          <p className="mt-5 max-w-2xl text-white/85 md:text-lg">
            LeTrusto helps you compare trade-offs, understand value, and pick confidently with AI-backed recommendations.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/ai" className="rounded-xl bg-white px-5 py-3 text-sm font-bold text-indigo-700">
              Ask AI Advisor
            </Link>
            <Link href="/compare" className="rounded-xl border border-white/40 px-5 py-3 text-sm font-semibold text-white">
              Open Comparison Lab
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto mt-8 max-w-7xl px-6 md:mt-10">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Subcategories</h2>
        <div className="mt-3 flex flex-wrap gap-2.5">
          {SUBCATEGORY_CHIPS.map((chip) => (
            <Link
              key={chip.label}
              href={`/category/electronics?sub=${chip.value}`}
              className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${sub === chip.value ? "border-violet-500 bg-violet-600 text-white" : "border-slate-200 bg-white text-slate-700 hover:border-violet-300 hover:text-violet-700"}`}
            >
              {chip.label}
            </Link>
          ))}
          <Link
            href="/category/electronics"
            className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${sub === "all" ? "border-slate-900 bg-slate-900 text-white" : "border-slate-200 bg-white text-slate-700 hover:border-slate-400 hover:text-slate-900"}`}
          >
            All
          </Link>
        </div>
      </section>

      <section className="mx-auto mt-8 max-w-7xl px-6 md:mt-10">
        <form className="grid gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-4" method="get">
          <input type="hidden" name="sub" value={sub} />
          <label className="text-sm font-semibold text-slate-700">
            Search
            <input
              name="q"
              defaultValue={q}
              placeholder="iphone, creator laptop, ANC headphones"
              className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-violet-400"
            />
          </label>

          <label className="text-sm font-semibold text-slate-700">
            Category Filter
            <select name="sub" defaultValue={sub} className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-violet-400">
              <option value="all">All electronics</option>
              <option value="phone">Phones</option>
              <option value="laptop">Laptops</option>
              <option value="headphones">Audio</option>
              <option value="smartwatch">Wearables</option>
              <option value="camera">Camera</option>
              <option value="gaming">Gaming</option>
              <option value="television">TV</option>
              <option value="tablet">Accessories</option>
            </select>
          </label>

          <label className="text-sm font-semibold text-slate-700">
            Minimum AI Score
            <select name="minAi" defaultValue={String(minAi)} className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-violet-400">
              <option value="0">Any score</option>
              <option value="85">85+</option>
              <option value="90">90+</option>
              <option value="94">94+</option>
            </select>
          </label>

          <div className="flex items-end gap-2">
            <button type="submit" className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-2.5 text-sm font-bold text-white">
              Apply Filters
            </button>
            <Link href="/category/electronics" className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700">
              Reset
            </Link>
          </div>
        </form>
      </section>

      <section className="mx-auto mt-14 max-w-7xl px-6">
        <h2 className="text-3xl font-black tracking-tight text-slate-900">Popular Comparisons</h2>
        <div className="mt-5 grid gap-4 lg:grid-cols-3">
          {FEATURED_COMPARISONS.map((item) => (
            <Link key={item.title} href={item.href} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
              <h3 className="text-xl font-black tracking-tight text-slate-900">{item.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{item.description}</p>
              <span className="mt-4 inline-flex text-sm font-semibold text-violet-700">Open comparison</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="mx-auto mt-14 max-w-7xl px-6">
        <h2 className="text-3xl font-black tracking-tight text-slate-900">Buying Guides</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {BUYING_GUIDES.map((guide) => (
            <Link key={guide.title} href={guide.href} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
              <p className="text-xs font-semibold uppercase tracking-wide text-violet-600">Guide</p>
              <h3 className="mt-2 text-xl font-black tracking-tight text-slate-900">{guide.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{guide.excerpt}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className="mx-auto mt-16 max-w-7xl px-6">
        <div className="mb-7 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-3xl font-black tracking-tight text-slate-900">AI Ranked Recommendations</h2>
            <p className="mt-1 text-sm text-slate-500">{electronicsProducts.length} products matched your research criteria.</p>
          </div>
        </div>

        {electronicsProducts.length > 0 ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {electronicsProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                highlightLabel="AI Ranked"
                aiHighlights={product.pros.slice(0, 3)}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-3xl border border-slate-200 bg-white p-8 text-center">
            <h3 className="text-xl font-bold text-slate-900">No products matched these filters.</h3>
            <p className="mt-2 text-sm text-slate-600">Try a broader category or lower minimum AI score.</p>
          </div>
        )}
      </section>
    </main>
  );
}
