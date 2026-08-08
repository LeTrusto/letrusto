import type { Metadata } from "next";

import ProductCard from "@/components/ProductCard";
import SchemaOrg from "@/components/SchemaOrg";
import SearchEnhancements from "@/components/SearchEnhancements";
import {
  getCatalogMetadata,
  getProductSearch,
  type ProductAiScoreFilter,
  type ProductFilterState,
  type ProductPriceFilter,
  type ProductQueryOptions,
  type ProductRatingFilter,
  type ProductSortOption,
} from "@/services/product.service";
import { getSearchParamValue } from "@/utils/helpers";

export const metadata: Metadata = {
  title: "Search",
  description: "Search and filter products across categories, brands, price bands, and AI scores.",
  robots: {
    index: false,
    follow: true,
  },
  alternates: {
    canonical: "/search",
  },
  openGraph: {
    title: "Search",
    description: "Search and filter products across categories, brands, price bands, and AI scores.",
    url: "/search",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Search",
    description: "Search and filter products across categories, brands, price bands, and AI scores.",
    images: ["/images/og-default.svg"],
  },
};

function parseNumberParam(value: string, fallback: number) {
  const parsed = Number(value);

  if (!Number.isFinite(parsed) || parsed < 1) {
    return fallback;
  }

  return Math.floor(parsed);
}

function buildSearchHref(options: ProductQueryOptions) {
  const searchParams = new URLSearchParams();

  if (options.q) {
    searchParams.set("q", options.q);
  }

  if (options.sortBy) {
    searchParams.set("sort", options.sortBy);
  }

  if (options.category && options.category !== "all") {
    searchParams.set("category", options.category);
  }

  if (options.price && options.price !== "all") {
    searchParams.set("price", options.price);
  }

  if (options.rating && options.rating !== "all") {
    searchParams.set("rating", options.rating);
  }

  if (options.aiScore && options.aiScore !== "all") {
    searchParams.set("aiScore", options.aiScore);
  }

  if (options.brand) {
    searchParams.set("brand", options.brand);
  }

  if (options.minPrice !== undefined) {
    searchParams.set("minPrice", String(options.minPrice));
  }

  if (options.maxPrice !== undefined) {
    searchParams.set("maxPrice", String(options.maxPrice));
  }

  if (options.minRating !== undefined) {
    searchParams.set("minRating", String(options.minRating));
  }

  if (options.minAiScore !== undefined) {
    searchParams.set("minAiScore", String(options.minAiScore));
  }

  if (options.page) {
    searchParams.set("page", String(options.page));
  }

  if (options.pageSize) {
    searchParams.set("pageSize", String(options.pageSize));
  }

  const query = searchParams.toString();
  return query ? `/search?${query}` : "/search";
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{
    q?: string | string[];
    sort?: string | string[];
    category?: string | string[];
    price?: string | string[];
    rating?: string | string[];
    aiScore?: string | string[];
    brand?: string | string[];
    minPrice?: string | string[];
    maxPrice?: string | string[];
    minRating?: string | string[];
    minAiScore?: string | string[];
    page?: string | string[];
    pageSize?: string | string[];
  }>;
}) {
  const params = await searchParams;

  const query = getSearchParamValue(params.q);
  const sortBy = (getSearchParamValue(params.sort, "relevance") as ProductSortOption);
  const brand = getSearchParamValue(params.brand);
  const minPrice = getSearchParamValue(params.minPrice);
  const maxPrice = getSearchParamValue(params.maxPrice);
  const minRating = getSearchParamValue(params.minRating);
  const minAiScore = getSearchParamValue(params.minAiScore);
  const page = parseNumberParam(getSearchParamValue(params.page, "1"), 1);
  const pageSize = parseNumberParam(getSearchParamValue(params.pageSize, "12"), 12);
  const filters: ProductFilterState = {
    category: getSearchParamValue(params.category, "all") as ProductFilterState["category"],
    price: getSearchParamValue(params.price, "all") as ProductPriceFilter,
    rating: getSearchParamValue(params.rating, "all") as ProductRatingFilter,
    aiScore: getSearchParamValue(params.aiScore, "all") as ProductAiScoreFilter,
  };
  const [metadata, search] = await Promise.all([
    getCatalogMetadata(),
    getProductSearch({
      q: query,
      sortBy,
      category: filters.category,
      price: filters.price,
      rating: filters.rating,
      aiScore: filters.aiScore,
      brand: brand || undefined,
      minPrice: minPrice ? Number(minPrice) : undefined,
      maxPrice: maxPrice ? Number(maxPrice) : undefined,
      minRating: minRating ? Number(minRating) : undefined,
      minAiScore: minAiScore ? Number(minAiScore) : undefined,
      page,
      pageSize,
    }),
  ]);

  const results = search.items;
  const pagination = search.pagination;
  const pageOptions = [12, 24, 36];
  const hasResults = results.length > 0;

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(125,211,252,0.12),_transparent_24%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)] px-5 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <SchemaOrg
          type="WebPage"
          data={{
            name: "Search",
            url: "https://letrusto.com/search",
            description: "Search and filter products across categories, brands, price bands, and AI scores.",
          }}
        />

        <div className="mb-10 flex flex-col gap-4 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-400">
              Product Discovery
            </p>
            <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950">Search Results</h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              {query ? (
                <>
                  Showing {pagination.totalItems} result{pagination.totalItems === 1 ? "" : "s"} for <span className="font-semibold text-slate-950">{query}</span>.
                </>
              ) : (
                <>
                  Browse all {pagination.totalItems} curated products and refine by category, price, rating, or recommendation score.
                </>
              )}
            </p>
          </div>

          <div className="rounded-2xl bg-slate-100 px-5 py-4 text-sm text-slate-700">
            Sort: <span className="font-semibold capitalize">{sortBy.replace("-", " ")}</span>
          </div>
        </div>

        <SearchEnhancements query={query} />

        <form className="mb-10 grid gap-4 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-6" method="get">
          <div className="lg:col-span-2">
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="q">
              Search
            </label>
            <input
              id="q"
              name="q"
              defaultValue={query}
              list="search-page-suggestions"
              placeholder="Search products, brands or ask a buying question..."
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100"
            />
            <datalist id="search-page-suggestions">
              {results.slice(0, 20).map((product) => (
                <option key={product.id} value={product.name} />
              ))}
            </datalist>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="sort">
              Sort By
            </label>
            <select id="sort" name="sort" defaultValue={sortBy} className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100">
              <option value="relevance">Relevance</option>
              <option value="price-low">Lowest Price</option>
              <option value="price-high">Highest Price</option>
              <option value="rating-high">Highest Rating</option>
              <option value="ai-high">Highest AI Score</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="category">
              Category
            </label>
            <select id="category" name="category" defaultValue={filters.category} className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100">
              <option value="all">All</option>
              {Object.entries(metadata.categoryPluralLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="price">
              Price
            </label>
            <select id="price" name="price" defaultValue={filters.price} className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100">
              <option value="all">All Prices</option>
              <option value="under-30000">Under ₹30,000</option>
              <option value="30000-80000">₹30,000-₹80,000</option>
              <option value="above-80000">Above ₹80,000</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="rating">
              Rating
            </label>
            <select id="rating" name="rating" defaultValue={filters.rating} className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100">
              <option value="all">All Ratings</option>
              <option value="4-plus">4+</option>
              <option value="4.5-plus">4.5+</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="aiScore">
              Recommendation Score
            </label>
            <select id="aiScore" name="aiScore" defaultValue={filters.aiScore} className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100">
              <option value="all">All Scores</option>
              <option value="above-90">Above 90</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="brand">
              Brand
            </label>
            <select id="brand" name="brand" defaultValue={brand || ""} className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100">
              <option value="">All Brands</option>
              {metadata.brands.map((brandName) => (
                <option key={brandName} value={brandName}>
                  {brandName}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="minPrice">
              Min Price
            </label>
            <input
              id="minPrice"
              name="minPrice"
              defaultValue={minPrice}
              type="number"
              min={0}
              placeholder="0"
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="maxPrice">
              Max Price
            </label>
            <input
              id="maxPrice"
              name="maxPrice"
              defaultValue={maxPrice}
              type="number"
              min={0}
              placeholder="250000"
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="minRating">
              Min Rating
            </label>
            <input
              id="minRating"
              name="minRating"
              defaultValue={minRating}
              type="number"
              min={0}
              max={5}
              step="0.1"
              placeholder="4.0"
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="pageSize">
              Page Size
            </label>
            <select id="pageSize" name="pageSize" defaultValue={String(pageSize)} className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100">
              {pageOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="lg:col-span-6 flex flex-wrap gap-3 pt-2">
            <button className="rounded-2xl bg-slate-950 px-6 py-3 font-semibold text-white transition hover:bg-slate-800" type="submit">
              Apply Filters
            </button>
            <a href="/search" className="rounded-2xl border border-slate-200 px-6 py-3 font-semibold text-slate-700 transition hover:bg-slate-50">
              Reset
            </a>
          </div>
        </form>

        {hasResults ? (
          <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
            {results.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                highlightLabel={query ? "Discovery Match" : metadata.productSpotlightBadges[product.id]}
              />
            ))}
          </div>
        ) : null}

        {pagination.totalPages > 1 ? (
          <div className="mt-10 flex flex-wrap items-center justify-center gap-3 rounded-3xl border border-slate-200 bg-white p-4">
            <a
              href={buildSearchHref({
                q: query,
                sortBy,
                category: filters.category,
                price: filters.price,
                rating: filters.rating,
                aiScore: filters.aiScore,
                brand: brand || undefined,
                minPrice: minPrice ? Number(minPrice) : undefined,
                maxPrice: maxPrice ? Number(maxPrice) : undefined,
                minRating: minRating ? Number(minRating) : undefined,
                minAiScore: minAiScore ? Number(minAiScore) : undefined,
                page: Math.max(1, pagination.page - 1),
                pageSize,
              })}
              className={`rounded-xl px-4 py-2 font-semibold ${pagination.hasPreviousPage ? "border border-slate-200 text-slate-700 hover:bg-slate-50" : "pointer-events-none border border-gray-100 text-gray-300"}`}
            >
              Previous
            </a>

            <span className="rounded-xl bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
              Page {pagination.page} of {pagination.totalPages}
            </span>

            <a
              href={buildSearchHref({
                q: query,
                sortBy,
                category: filters.category,
                price: filters.price,
                rating: filters.rating,
                aiScore: filters.aiScore,
                brand: brand || undefined,
                minPrice: minPrice ? Number(minPrice) : undefined,
                maxPrice: maxPrice ? Number(maxPrice) : undefined,
                minRating: minRating ? Number(minRating) : undefined,
                minAiScore: minAiScore ? Number(minAiScore) : undefined,
                page: Math.min(pagination.totalPages, pagination.page + 1),
                pageSize,
              })}
              className={`rounded-xl px-4 py-2 font-semibold ${pagination.hasNextPage ? "border border-slate-200 text-slate-700 hover:bg-slate-50" : "pointer-events-none border border-gray-100 text-gray-300"}`}
            >
              Next
            </a>
          </div>
        ) : null}

        {!hasResults && (
          <div className="mt-16 rounded-[2rem] border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-950">No products matched your filters.</h2>
            <p className="mt-3">Adjust the search term, widen the price range, or clear filters to discover more relevant options.</p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <a href="/search" className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-800">
                Reset search
              </a>
              <a href="/guides" className="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
                Explore guides
              </a>
            </div>
          </div>
        )}

      </div>
    </main>
  );
}