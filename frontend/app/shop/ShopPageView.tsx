"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { SlidersHorizontal, X } from "lucide-react";
import { CATEGORY_MAP, type CommerceCategory } from "@/types/commerce";
import CommerceProductCard from "@/components/products/CommerceProductCard";
import { getPublicProducts, toCommerceProduct } from "@/services/product.service";

const SORT_OPTIONS = [
  { value: "recommended", label: "Recommended" },
  { value: "price-asc", label: "Price: Low to High" },
  { value: "price-desc", label: "Price: High to Low" },
  { value: "newest", label: "Newest First" },
] as const;

const CATEGORIES = Object.entries(CATEGORY_MAP) as [CommerceCategory, string][];

export default function ShopPageView() {
  const searchParams = useSearchParams();
  const initialCategory = searchParams.get("category") as CommerceCategory | null;
  const initialQuery = searchParams.get("q") ?? "";
  const initialMaxPrice = searchParams.get("maxPrice");

  const [selectedCategory, setCategory] = useState<CommerceCategory | null>(initialCategory);
  const [sortBy, setSortBy] = useState<string>("recommended");
  const [query, setQuery] = useState(initialQuery);
  const [maxPrice, setMaxPrice] = useState<number | null>(initialMaxPrice ? Number(initialMaxPrice) : null);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [products, setProducts] = useState<ReturnType<typeof toCommerceProduct>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void getPublicProducts()
      .then((catalog) => {
        if (!cancelled) setProducts(catalog.map(toCommerceProduct));
      })
      .catch(() => {
        if (!cancelled) setError("The live catalog is temporarily unavailable.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const filtered = useMemo(() => {
    let result = [...products];

    if (selectedCategory) {
      result = result.filter((p) => p.category === selectedCategory);
    }

    if (query.trim()) {
      const q = query.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(q) ||
          p.description.toLowerCase().includes(q) ||
          p.tags.some((t) => t.toLowerCase().includes(q))
      );
    }

    if (maxPrice) {
      result = result.filter((p) => p.price <= maxPrice);
    }

    switch (sortBy) {
      case "price-asc":
        result.sort((a, b) => a.price - b.price);
        break;
      case "price-desc":
        result.sort((a, b) => b.price - a.price);
        break;
      case "newest":
        result.sort((a, b) => (b.isNewDrop ? 1 : 0) - (a.isNewDrop ? 1 : 0));
        break;
    }

    return result;
  }, [products, selectedCategory, sortBy, query, maxPrice]);

  const activeFilterCount = [selectedCategory, maxPrice, query.trim()].filter(Boolean).length;

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 md:py-10">
      {/* Header */}
      <div className="flex min-w-0 flex-wrap items-center justify-between gap-3 mb-6">
        <div className="min-w-0">
          <h1 className="lt-heading-2">
            {selectedCategory ? CATEGORY_MAP[selectedCategory] : "All Products"}
          </h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">{loading ? "Loading catalog..." : `${filtered.length} products`}</p>
        </div>
        <div className="flex max-w-full shrink-0 items-center gap-3">
          <button
            onClick={() => setFiltersOpen(!filtersOpen)}
            className="lt-btn lt-btn-sm lt-btn-secondary md:hidden relative"
          >
            <SlidersHorizontal size={14} />
            Filters
            {activeFilterCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--lt-primary)] text-white text-[10px] rounded-full flex items-center justify-center">
                {activeFilterCount}
              </span>
            )}
          </button>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="lt-select text-sm"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex gap-8">
        {/* Sidebar filters — desktop always visible, mobile toggleable */}
        <aside className={`${filtersOpen ? "fixed inset-0 z-50 bg-white p-4 overflow-y-auto" : "hidden"} md:block md:static md:w-56 shrink-0`}>
          <div className="flex items-center justify-between md:hidden mb-4">
            <h2 className="font-bold text-lg">Filters</h2>
            <button onClick={() => setFiltersOpen(false)} aria-label="Close filters">
              <X size={20} />
            </button>
          </div>

          {/* Search */}
          <div className="mb-5">
            <label htmlFor="shop-search" className="lt-label mb-1.5 block">Search</label>
            <input
              id="shop-search"
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search products..."
              className="lt-input"
            />
          </div>

          {/* Category */}
          <div className="mb-5">
            <h3 className="lt-label mb-2">Category</h3>
            <div className="space-y-1.5">
              <button
                onClick={() => setCategory(null)}
                className={`block w-full text-left text-sm px-2 py-1 rounded ${!selectedCategory ? "font-semibold text-[var(--text-primary)] bg-[var(--surface-muted)]" : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"}`}
              >
                All
              </button>
              {CATEGORIES.map(([id, label]) => (
                <button
                  key={id}
                  onClick={() => setCategory(id)}
                  className={`block w-full text-left text-sm px-2 py-1 rounded ${selectedCategory === id ? "font-semibold text-[var(--text-primary)] bg-[var(--surface-muted)]" : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"}`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Price range */}
          <div className="mb-5">
            <h3 className="lt-label mb-2">Max Price</h3>
            <div className="flex flex-wrap gap-2">
              {[null, 199, 299, 499, 999].map((price) => (
                <button
                  key={price ?? "all"}
                  onClick={() => setMaxPrice(price)}
                  className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                    maxPrice === price
                      ? "border-[var(--lt-primary)] bg-[var(--lt-primary)] text-white"
                      : "border-[var(--border)] hover:border-[var(--border-hover)]"
                  }`}
                >
                  {price ? `₹${price}` : "Any"}
                </button>
              ))}
            </div>
          </div>

          {activeFilterCount > 0 && (
            <button
              onClick={() => { setCategory(null); setMaxPrice(null); setQuery(""); }}
              className="lt-btn lt-btn-sm lt-btn-ghost text-[var(--lt-rose)] w-full mt-2"
            >
              Clear All Filters
            </button>
          )}

          {/* Close button mobile */}
          <button
            onClick={() => setFiltersOpen(false)}
            className="lt-btn lt-btn-md lt-btn-primary w-full mt-4 md:hidden"
          >
            Show {filtered.length} Products
          </button>
        </aside>

        {/* Product grid */}
        <div className="flex-1">
          {loading ? (
            <div className="text-center py-20"><p className="text-sm text-[var(--text-muted)]">Loading live products...</p></div>
          ) : error ? (
            <div className="text-center py-20"><p className="text-lg font-semibold text-[var(--text-primary)]">Catalog unavailable</p><p className="text-sm text-[var(--text-muted)] mt-1">{error}</p></div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-lg font-semibold text-[var(--text-primary)]">No products found</p>
              <p className="text-sm text-[var(--text-muted)] mt-1">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {filtered.map((product) => (
                <CommerceProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
