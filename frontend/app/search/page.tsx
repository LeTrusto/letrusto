import ProductCard from "@/components/ProductCard";
import SearchEnhancements from "@/components/SearchEnhancements";
import { filterProducts } from "@/lib/filterProducts";
import { categoryPluralLabels, productSpotlightBadges } from "@/lib/products";
import { discoverProducts } from "@/lib/recommendations";
import { sortProducts } from "@/lib/sortProducts";
import { products } from "@/lib/products";
import type { ProductAiScoreFilter, ProductFilterState, ProductPriceFilter, ProductRatingFilter, ProductSortOption } from "@/types/products";
import { getSearchParamValue } from "@/utils/helpers";

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
  }>;
}) {
  const params = await searchParams;

  const query = getSearchParamValue(params.q);
  const sortBy = (getSearchParamValue(params.sort, "relevance") as ProductSortOption);
  const filters: ProductFilterState = {
    category: getSearchParamValue(params.category, "all") as ProductFilterState["category"],
    price: getSearchParamValue(params.price, "all") as ProductPriceFilter,
    rating: getSearchParamValue(params.rating, "all") as ProductRatingFilter,
    aiScore: getSearchParamValue(params.aiScore, "all") as ProductAiScoreFilter,
  };

  const discoveredProducts = discoverProducts(query);
  const filteredProducts = filterProducts(discoveredProducts, filters);
  const results = sortProducts(filteredProducts, sortBy, query);

  return (
    <main className="min-h-screen bg-gray-50 p-10">
      <div className="max-w-7xl mx-auto">

        <div className="mb-10 flex flex-col gap-4 rounded-[2rem] border border-purple-100 bg-white p-8 shadow-xl shadow-purple-100/40 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-purple-500">
              Product Discovery
            </p>
            <h1 className="mt-3 text-4xl font-bold text-gray-900">Search Results</h1>
            <p className="mt-3 text-gray-500">
              {query ? (
                <>
                  Showing {results.length} result{results.length === 1 ? "" : "s"} for <span className="font-semibold text-gray-900">{query}</span>.
                </>
              ) : (
                <>
                  Browse all {results.length} curated products and refine by category, price, rating, or AI score.
                </>
              )}
            </p>
          </div>

          <div className="rounded-2xl bg-purple-50 px-5 py-4 text-sm text-purple-700">
            Sort: <span className="font-semibold capitalize">{sortBy.replace("-", " ")}</span>
          </div>
        </div>

        <SearchEnhancements query={query} />

        <form className="mb-10 grid gap-4 rounded-[2rem] border border-purple-100 bg-white p-6 shadow-sm lg:grid-cols-6" method="get">
          <div className="lg:col-span-2">
            <label className="mb-2 block text-sm font-semibold text-gray-700" htmlFor="q">
              Search
            </label>
            <input
              id="q"
              name="q"
              defaultValue={query}
              list="search-page-suggestions"
              placeholder="iphone, coding laptop, music"
              className="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none transition focus:border-purple-400"
            />
            <datalist id="search-page-suggestions">
              {products.slice(0, 20).map((product) => (
                <option key={product.id} value={product.name} />
              ))}
            </datalist>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-gray-700" htmlFor="sort">
              Sort By
            </label>
            <select id="sort" name="sort" defaultValue={sortBy} className="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none transition focus:border-purple-400">
              <option value="relevance">Relevance</option>
              <option value="price-low">Lowest Price</option>
              <option value="price-high">Highest Price</option>
              <option value="rating-high">Highest Rating</option>
              <option value="ai-high">Highest AI Score</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-gray-700" htmlFor="category">
              Category
            </label>
            <select id="category" name="category" defaultValue={filters.category} className="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none transition focus:border-purple-400">
              <option value="all">All</option>
              {Object.entries(categoryPluralLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-gray-700" htmlFor="price">
              Price
            </label>
            <select id="price" name="price" defaultValue={filters.price} className="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none transition focus:border-purple-400">
              <option value="all">All Prices</option>
              <option value="under-30000">Under ₹30,000</option>
              <option value="30000-80000">₹30,000-₹80,000</option>
              <option value="above-80000">Above ₹80,000</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-gray-700" htmlFor="rating">
              Rating
            </label>
            <select id="rating" name="rating" defaultValue={filters.rating} className="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none transition focus:border-purple-400">
              <option value="all">All Ratings</option>
              <option value="4-plus">4+</option>
              <option value="4.5-plus">4.5+</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-gray-700" htmlFor="aiScore">
              AI Score
            </label>
            <select id="aiScore" name="aiScore" defaultValue={filters.aiScore} className="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none transition focus:border-purple-400">
              <option value="all">All Scores</option>
              <option value="above-90">Above 90</option>
            </select>
          </div>

          <div className="lg:col-span-6 flex flex-wrap gap-3 pt-2">
            <button className="rounded-2xl bg-gradient-to-r from-fuchsia-600 to-purple-600 px-6 py-3 font-semibold text-white transition hover:from-fuchsia-700 hover:to-purple-700" type="submit">
              Apply Filters
            </button>
            <a href="/search" className="rounded-2xl border border-gray-200 px-6 py-3 font-semibold text-gray-700 transition hover:bg-gray-50">
              Reset
            </a>
          </div>
        </form>

        <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
          {results.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              highlightLabel={query ? "Discovery Match" : productSpotlightBadges[product.id]}
            />
          ))}
        </div>

        {results.length === 0 && (
          <div className="mt-16 rounded-[2rem] border border-dashed border-purple-200 bg-white p-10 text-center text-gray-500 shadow-lg shadow-purple-100/30">
            <h2 className="text-2xl font-bold text-gray-900">No products matched your filters.</h2>
            <p className="mt-3">Adjust the search term, widen the price range, or clear the filters to discover more products.</p>
          </div>
        )}

      </div>
    </main>
  );
}