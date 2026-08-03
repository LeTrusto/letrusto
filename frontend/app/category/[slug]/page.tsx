import type { Metadata } from "next";
import Link from "next/link";
import ProductCard from "@/components/ProductCard";
import { getProductSearch, getCatalogMetadata } from "@/services/product.service";
import { CATALOG_TREE, getCategoryLabel } from "@/constants/index";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const label = getCategoryLabel(slug);
  return {
    title: `${label} — LeTrusto`,
    description: `Browse the best ${label} with AI-powered comparisons and honest reviews.`,
  };
}

const CATEGORY_HEROES: Record<string, { icon: string; description: string; color: string }> = {
  smartphones: { icon: "📱", description: "Find the perfect smartphone — AI-ranked by camera, battery, performance and value.", color: "from-blue-600 to-indigo-700" },
  laptop: { icon: "💻", description: "Compare laptops for coding, work, gaming and study with our AI advisor.", color: "from-violet-600 to-purple-700" },
  headphones: { icon: "🎧", description: "Discover the best headphones and earbuds — noise-cancelling, wireless and studio.", color: "from-pink-600 to-rose-700" },
  smartwatch: { icon: "⌚", description: "Track your fitness and stay connected with the right smartwatch for your lifestyle.", color: "from-emerald-600 to-teal-700" },
  camera: { icon: "📷", description: "Find your perfect camera — mirrorless, DSLR, compact or action.", color: "from-amber-600 to-orange-700" },
  gaming: { icon: "🎮", description: "Level up with the best consoles, handhelds and gaming accessories.", color: "from-red-600 to-rose-700" },
  television: { icon: "📺", description: "Choose from OLED, QLED and 4K TVs for cinema-quality home entertainment.", color: "from-cyan-600 to-sky-700" },
  tablet: { icon: "📲", description: "The best tablets for students, creators and professionals.", color: "from-fuchsia-600 to-pink-700" },
  "web-hosting": { icon: "🌐", description: "Compare web hosting plans and SaaS tools — AI picks the best for your needs.", color: "from-green-600 to-emerald-700" },
  refrigerator: { icon: "🧊", description: "Find the right refrigerator for your family — energy efficient and feature packed.", color: "from-sky-600 to-blue-700" },
  "washing-machine": { icon: "🫧", description: "Compare washing machines by capacity, programs and energy rating.", color: "from-teal-600 to-cyan-700" },
};

export default async function CategoryPage({ params }: Props) {
  const { slug } = await params;
  const hero = CATEGORY_HEROES[slug];
  const label = getCategoryLabel(slug);

  const [searchResult, metadata] = await Promise.all([
    getProductSearch({ category: slug, pageSize: 24, sortBy: "ai-high" }),
    getCatalogMetadata(),
  ]);

  const products = searchResult.items;

  // Find related categories (siblings in the same parent)
  const parent = CATALOG_TREE.find((t) => t.children?.some((c) => c.slug === slug));
  const siblingCategories = parent?.children?.filter((c) => c.slug !== slug).slice(0, 5) ?? [];

  return (
    <main className="min-h-screen bg-white">
      {/* Hero */}
      <div className={`bg-gradient-to-br ${hero?.color ?? "from-purple-600 to-pink-700"} py-14 text-white`}>
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex items-center gap-4">
            <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/20 text-4xl backdrop-blur-sm">
              {hero?.icon ?? "🛒"}
            </span>
            <div>
              <p className="text-sm font-semibold uppercase tracking-widest opacity-80">Category</p>
              <h1 className="text-3xl font-black md:text-4xl">{label}</h1>
            </div>
          </div>
          {hero?.description && (
            <p className="mt-4 max-w-2xl text-lg opacity-90">{hero.description}</p>
          )}
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Link
              href={`/ai?q=Best ${label}`}
              className="rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-purple-700 transition hover:bg-white/90"
            >
              ✨ Ask AI for {label}
            </Link>
            <Link
              href={`/search?category=${slug}`}
              className="rounded-xl border border-white/40 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-white/10"
            >
              All {label} →
            </Link>
          </div>
        </div>
      </div>

      {/* Related categories */}
      {siblingCategories.length > 0 && (
        <div className="border-b border-gray-100 bg-gray-50">
          <div className="mx-auto flex max-w-7xl gap-2 overflow-x-auto px-6 py-3">
            {siblingCategories.map((cat) => (
              <Link
                key={cat.slug}
                href={`/category/${cat.slug}`}
                className="shrink-0 rounded-full border border-gray-200 bg-white px-4 py-1.5 text-sm font-medium text-gray-600 transition hover:border-purple-300 hover:text-purple-700"
              >
                {cat.icon} {cat.name}
              </Link>
            ))}
          </div>
        </div>
      )}

      <div className="mx-auto max-w-7xl px-6 py-10">
        {/* Count + sort */}
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              {searchResult.pagination.totalItems} {label} Products
            </h2>
            <p className="text-sm text-gray-500">Sorted by AI Score — highest rated first</p>
          </div>
          <Link
            href={`/search?category=${slug}`}
            className="text-sm font-semibold text-purple-700 hover:underline"
          >
            Advanced filters →
          </Link>
        </div>

        {/* Product grid */}
        {products.length > 0 ? (
          <div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
            {products.map((product, i) => (
              <ProductCard
                key={product.id}
                product={product}
                priority={i < 4}
                highlightLabel={
                  metadata.productSpotlightBadges[product.id] ??
                  (i === 0 ? "AI Pick" : i < 4 ? "Top Rated" : undefined)
                }
              />
            ))}
          </div>
        ) : (
          <div className="py-20 text-center">
            <span className="text-6xl">{hero?.icon ?? "🔍"}</span>
            <h3 className="mt-4 text-xl font-bold text-gray-900">No products found</h3>
            <p className="mt-2 text-gray-500">
              We&apos;re adding {label} products soon. Try a different category or use AI.
            </p>
            <Link
              href="/ai"
              className="mt-6 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 text-sm font-bold text-white"
            >
              ✨ Ask AI Advisor
            </Link>
          </div>
        )}

        {/* Pagination hint */}
        {searchResult.pagination.hasNextPage && (
          <div className="mt-10 text-center">
            <Link
              href={`/search?category=${slug}`}
              className="inline-flex items-center gap-2 rounded-xl border border-purple-200 bg-white px-6 py-3 text-sm font-semibold text-purple-700 transition hover:bg-purple-50"
            >
              View all {searchResult.pagination.totalItems} {label} products →
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
