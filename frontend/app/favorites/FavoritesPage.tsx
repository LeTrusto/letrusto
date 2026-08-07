"use client";

import { useMemo, useState } from "react";

import ProductCard from "@/components/ProductCard";
import { useFavorites } from "@/hooks/useFavorites";
import { useProducts } from "@/hooks/useProducts";
import { categoryLabels } from "@/lib/products";
import type { Product } from "@/services/product.service";

export default function FavoritesPage() {
  const { favoriteIds } = useFavorites();
  const { products } = useProducts();
  const [sortBy, setSortBy] = useState<"latest" | "price-low" | "price-high" | "rating-high">("latest");
  const [category, setCategory] = useState<"all" | Product["category"]>("all");

  const favoriteProducts = useMemo(() => {
    const base = favoriteIds
      .map((favoriteId) => products.find((product) => product.id === favoriteId))
      .filter((product): product is Product => Boolean(product));

    const filtered =
      category === "all"
        ? base
        : base.filter((product) => product.category === category);

    const sorted = [...filtered];

    switch (sortBy) {
      case "price-low":
        sorted.sort((a, b) => a.priceValue - b.priceValue);
        break;
      case "price-high":
        sorted.sort((a, b) => b.priceValue - a.priceValue);
        break;
      case "rating-high":
        sorted.sort((a, b) => b.rating - a.rating);
        break;
      case "latest":
      default:
        sorted.sort((a, b) => favoriteIds.indexOf(a.id) - favoriteIds.indexOf(b.id));
        break;
    }

    return sorted;
  }, [category, favoriteIds, products, sortBy]);

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-16">
      <div className="mx-auto max-w-7xl">
        <div className="mb-10 rounded-[2rem] border border-purple-100 bg-white p-8 shadow-lg shadow-purple-100/40">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-pink-500">Saved Picks</p>
          <h1 className="mt-3 text-4xl font-bold text-gray-900">Favorites</h1>
          <p className="mt-3 text-gray-500">
            {`You have ${favoriteProducts.length} saved product${favoriteProducts.length === 1 ? "" : "s"}.`}
          </p>

          <div className="mt-6 grid gap-3 md:grid-cols-3">
            <label className="text-sm font-semibold text-gray-700">
              Sort
              <select
                className="mt-2 w-full rounded-xl border border-gray-200 px-3 py-2"
                value={sortBy}
                onChange={(event) => setSortBy(event.target.value as typeof sortBy)}
              >
                <option value="latest">Latest Added</option>
                <option value="price-low">Lowest Price</option>
                <option value="price-high">Highest Price</option>
                <option value="rating-high">Highest Rating</option>
              </select>
            </label>

            <label className="text-sm font-semibold text-gray-700">
              Category
              <select
                className="mt-2 w-full rounded-xl border border-gray-200 px-3 py-2"
                value={category}
                onChange={(event) => setCategory(event.target.value as typeof category)}
              >
                <option value="all">All Categories</option>
                {Object.entries(categoryLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        {favoriteProducts.length > 0 ? (
          <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
            {favoriteProducts.map((product) => (
              <ProductCard key={product.id} product={product} highlightLabel="Favorite" />
            ))}
          </div>
        ) : (
          <div className="rounded-[2rem] border border-dashed border-purple-200 bg-white p-10 text-center shadow-lg shadow-purple-100/30">
            <div className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-full bg-pink-100 text-4xl">♡</div>
            <h2 className="text-2xl font-bold text-gray-900">No favorites yet.</h2>
            <p className="mt-3 text-gray-500">Tap the heart on any product card to save it here for later comparison.</p>
          </div>
        )}
      </div>
    </main>
  );
}
