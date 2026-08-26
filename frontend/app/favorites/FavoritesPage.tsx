"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Heart } from "lucide-react";

import ProductCard from "@/components/ProductCard";
import { useFavorites } from "@/hooks/useFavorites";
import { useProducts } from "@/hooks/useProducts";
import type { Product } from "@/services/product.service";

export default function FavoritesPage() {
  const { favoriteIds } = useFavorites();
  const { products } = useProducts();
  const [sortBy, setSortBy] = useState<"latest" | "price-low" | "price-high" | "rating-high">("latest");

  const favoriteProducts = useMemo(() => {
    const base = favoriteIds
      .map((favoriteId) => products.find((product) => product.id === favoriteId))
      .filter((product): product is Product => Boolean(product));

    const sorted = [...base];

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
  }, [favoriteIds, products, sortBy]);

  return (
    <main className="min-h-screen bg-[var(--surface-soft)] px-6 py-16">
      <div className="mx-auto max-w-7xl">
        <div className="lt-card mb-10 rounded-[var(--radius-2xl)] p-8">
            <p className="lt-label text-[var(--lt-purple)]">Saved Designs</p>
          <h1 className="lt-heading-1 mt-3">Favorites</h1>
          <p className="lt-body mt-3">
            {favoriteProducts.length > 0
              ? `You have ${favoriteProducts.length} saved item${favoriteProducts.length === 1 ? "" : "s"}.`
              : "Save designs and products you want to revisit."}
          </p>

          {favoriteProducts.length > 0 && (
            <div className="mt-6 max-w-xs">
              <label className="text-sm font-semibold text-[var(--text-primary)]">
                Sort
                <select
                  className="lt-select mt-2 w-full"
                  value={sortBy}
                  onChange={(event) => setSortBy(event.target.value as typeof sortBy)}
                >
                  <option value="latest">Latest Added</option>
                  <option value="price-low">Lowest Price</option>
                  <option value="price-high">Highest Price</option>
                  <option value="rating-high">Highest Rating</option>
                </select>
              </label>
            </div>
          )}
        </div>

        {favoriteProducts.length > 0 ? (
          <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
            {favoriteProducts.map((product) => (
              <ProductCard key={product.id} product={product} highlightLabel="Favorite" />
            ))}
          </div>
        ) : (
          <div className="lt-card rounded-[var(--radius-2xl)] border-dashed p-10 text-center">
            <div className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-full bg-[rgba(124,58,237,0.08)]">
              <Heart className="h-9 w-9 text-[var(--lt-purple)]" />
            </div>
            <h2 className="lt-heading-2">No favorites yet</h2>
            <p className="lt-body mx-auto mt-3 max-w-md">
              Tap the heart on any product card to save it here for later.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <Link href="/shop" className="lt-btn lt-btn-md lt-btn-primary">
                Browse Designs
              </Link>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
