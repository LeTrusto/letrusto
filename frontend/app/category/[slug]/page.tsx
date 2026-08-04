import type { Metadata } from "next";
import Link from "next/link";

import ProductCard from "@/components/ProductCard";
import { CATALOG_TREE, getCategoryLabel } from "@/constants/index";
import { getCatalogMetadata, getProductSearch } from "@/services/product.service";

type Props = { params: Promise<{ slug: string }> };

type CategoryDesign = {
  icon: string;
  description: string;
  gradientClass: string;
  eta?: string;
  planned?: string[];
};

const CATEGORY_DESIGN: Record<string, CategoryDesign> = {
  smartphones: {
    icon: "AI",
    description: "Find your ideal smartphone with camera, battery, and value-focused AI ranking.",
    gradientClass: "from-blue-600 to-indigo-700",
  },
  laptop: {
    icon: "LT",
    description: "Compare laptops for coding, business, and gaming with transparent scorecards.",
    gradientClass: "from-violet-600 to-purple-700",
  },
  headphones: {
    icon: "AU",
    description: "Discover audio picks tuned for commute, calls, and studio quality.",
    gradientClass: "from-fuchsia-600 to-rose-700",
  },
  smartwatch: {
    icon: "SW",
    description: "Choose wearables by health tracking quality, battery endurance, and reliability.",
    gradientClass: "from-emerald-600 to-teal-700",
  },
  camera: {
    icon: "CM",
    description: "Explore creator-first camera recommendations sorted by practical use cases.",
    gradientClass: "from-amber-600 to-orange-700",
  },
  gaming: {
    icon: "GM",
    description: "Level up with gaming picks ranked by performance, ecosystem, and long-term value.",
    gradientClass: "from-red-600 to-rose-700",
  },
  television: {
    icon: "TV",
    description: "Find the right 4K and OLED TVs with room-size and viewing-profile guidance.",
    gradientClass: "from-cyan-600 to-sky-700",
  },
  tablet: {
    icon: "TB",
    description: "Compare tablets for productivity, study, creativity, and entertainment.",
    gradientClass: "from-indigo-600 to-violet-700",
  },
  "home-kitchen": {
    icon: "HK",
    description: "Practical appliance choices for real homes, not spec-sheet hype.",
    gradientClass: "from-slate-700 to-slate-900",
  },
  refrigerator: {
    icon: "RF",
    description: "Choose refrigerators by storage design, efficiency, and family-size fit.",
    gradientClass: "from-sky-600 to-blue-700",
  },
  "washing-machine": {
    icon: "WM",
    description: "Compare washing machines by wash quality, reliability, and daily usability.",
    gradientClass: "from-teal-600 to-cyan-700",
  },
  hosting: {
    icon: "HOST",
    description: "Infrastructure buying assistant for hosting plans, uptime goals, and growth stages.",
    gradientClass: "from-indigo-700 to-cyan-700",
    eta: "Q4 2026",
    planned: [
      "Uptime and support quality benchmarks",
      "Shared, cloud, and managed hosting scorecards",
      "Renewal cost and scaling path intelligence",
    ],
  },
  saas: {
    icon: "SAAS",
    description: "AI SaaS advisor for team tooling, integrations, adoption, and cost control.",
    gradientClass: "from-emerald-700 to-teal-700",
    eta: "Q1 2027",
    planned: [
      "Role-based software fit recommendations",
      "Onboarding complexity and TCO scoring",
      "Vendor reliability and roadmap confidence",
    ],
  },
  beauty: {
    icon: "BEAUTY",
    description: "Ingredient-aware recommendations and routine builders are on the way.",
    gradientClass: "from-pink-700 to-rose-700",
    eta: "Q1 2027",
    planned: [
      "Skin-type and concern-based routine guidance",
      "Ingredient conflict and safety checks",
      "Budget-friendly regimen builder",
    ],
  },
  "pet-care": {
    icon: "PET",
    description: "Smarter buying workflows for pet food, care, and wellness essentials.",
    gradientClass: "from-amber-700 to-orange-700",
    eta: "Q2 2027",
    planned: [
      "Breed and life-stage aware recommendations",
      "Food quality and ingredient trust signals",
      "Vet-informed product buying guides",
    ],
  },
  fitness: {
    icon: "FIT",
    description: "Training and recovery buying advisor launches soon.",
    gradientClass: "from-lime-700 to-emerald-700",
    eta: "Q2 2027",
    planned: [
      "Goal-based equipment shortlists",
      "Home gym budget planning",
      "Wearable and accessory integration fit",
    ],
  },
  kitchen: {
    icon: "KIT",
    description: "AI-led kitchen buying guidance for modern homes is in development.",
    gradientClass: "from-sky-700 to-cyan-700",
    eta: "Q2 2027",
    planned: [
      "Space-aware kitchen appliance planning",
      "Energy efficiency and lifecycle comparisons",
      "Family cooking profile recommendations",
    ],
  },
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const label = getCategoryLabel(slug);
  return {
    title: `${label} | LeTrusto`,
    description: `Explore ${label} with LeTrusto AI buying intelligence, comparisons, and roadmap updates.`,
  };
}

function ComingSoonCategoryPage({ slug, label, design }: { slug: string; label: string; design: CategoryDesign }) {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50">
      <section className="mx-auto max-w-5xl px-6 py-18">
        <div className={`rounded-3xl border border-white/30 bg-gradient-to-br ${design.gradientClass} p-8 text-white shadow-2xl md:p-12`}>
          <p className="inline-flex rounded-full border border-white/30 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide">
            Coming Soon
          </p>
          <div className="mt-5 flex flex-wrap items-center gap-4">
            <div className="rounded-2xl border border-white/30 bg-white/10 px-4 py-3 text-sm font-black tracking-widest">
              {design.icon}
            </div>
            <h1 className="text-3xl font-black tracking-tight md:text-5xl">{label} Advisor</h1>
          </div>
          <p className="mt-4 max-w-3xl text-white/90 md:text-lg">{design.description}</p>
          <p className="mt-5 text-sm font-semibold text-white/90">Launch target: {design.eta ?? "Planned"}</p>
        </div>

        <div className="mt-8 rounded-3xl border border-slate-200 bg-white p-7 shadow-sm md:p-9">
          <h2 className="text-2xl font-black text-slate-900">What we are building</h2>
          <ul className="mt-4 space-y-2 text-sm text-slate-700 md:text-base">
            {(design.planned ?? []).map((item) => (
              <li key={`${slug}-${item}`} className="flex items-start gap-2">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-violet-600" />
                <span>{item}</span>
              </li>
            ))}
          </ul>

          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              href="/support?tab=contact&category=feedback"
              className="rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-5 py-3 text-sm font-bold text-white"
            >
              Notify Me
            </Link>
            <Link
              href="/"
              className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-500 hover:text-slate-900"
            >
              Back to Homepage
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}

export default async function CategoryPage({ params }: Props) {
  const { slug } = await params;
  const label = getCategoryLabel(slug);
  const design = CATEGORY_DESIGN[slug] ?? {
    icon: "CAT",
    description: `Explore ${label} recommendations and comparisons built for practical buying decisions.`,
    gradientClass: "from-slate-700 to-indigo-800",
  };

  const [searchResult, metadata] = await Promise.all([
    getProductSearch({ category: slug, pageSize: 24, sortBy: "ai-high" }),
    getCatalogMetadata(),
  ]);

  const products = searchResult.items;

  if (products.length === 0) {
    return <ComingSoonCategoryPage slug={slug} label={label} design={design} />;
  }

  const parent = CATALOG_TREE.find((node) => node.children?.some((child) => child.slug === slug));
  const siblingCategories = parent?.children?.filter((child) => child.slug !== slug).slice(0, 5) ?? [];

  return (
    <main className="min-h-screen bg-white">
      <section className={`bg-gradient-to-br ${design.gradientClass} py-14 text-white`}>
        <div className="mx-auto max-w-7xl px-6">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-white/70">AI Category Hub</p>
          <h1 className="mt-3 text-3xl font-black tracking-tight md:text-5xl">{label}</h1>
          <p className="mt-4 max-w-2xl text-white/90 md:text-lg">{design.description}</p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href={`/ai?q=Best ${label}`} className="rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-violet-700">
              Ask AI for {label}
            </Link>
            <Link href={`/search?category=${slug}`} className="rounded-xl border border-white/40 px-5 py-2.5 text-sm font-semibold text-white">
              Advanced filters
            </Link>
          </div>
        </div>
      </section>

      {siblingCategories.length > 0 ? (
        <section className="border-b border-slate-100 bg-slate-50">
          <div className="mx-auto flex max-w-7xl gap-2 overflow-x-auto px-6 py-3">
            {siblingCategories.map((cat) => (
              <Link key={cat.slug} href={`/category/${cat.slug}`} className="shrink-0 rounded-full border border-slate-200 bg-white px-4 py-1.5 text-sm font-semibold text-slate-600 hover:border-violet-300 hover:text-violet-700">
                {cat.name}
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-black tracking-tight text-slate-900">{searchResult.pagination.totalItems} products ranked by AI</h2>
            <p className="mt-1 text-sm text-slate-500">Trust signals, rating, and value are weighted in this ordering.</p>
          </div>
          <Link href={`/search?category=${slug}`} className="text-sm font-semibold text-violet-700 hover:underline">
            View all with filters
          </Link>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {products.map((product, index) => (
            <ProductCard
              key={product.id}
              product={product}
              priority={index < 4}
              aiReason={product.aiSummary}
              highlightLabel={metadata.productSpotlightBadges[product.id] ?? (index < 3 ? "Top Rated" : undefined)}
            />
          ))}
        </div>
      </section>
    </main>
  );
}
