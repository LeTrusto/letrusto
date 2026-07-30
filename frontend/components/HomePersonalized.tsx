"use client";

import ProductCard from "@/components/ProductCard";
import { useFavorites } from "@/hooks/useFavorites";
import { useRecentlyViewed } from "@/hooks/useRecentlyViewed";
import { products } from "@/lib/products";

function mapIdsToProducts(ids: string[]) {
  return ids
    .map((id) => products.find((product) => product.id === id))
    .filter((product): product is (typeof products)[number] => Boolean(product));
}

export default function HomePersonalized() {
  const { favoriteIds } = useFavorites();
  const { recentlyViewedIds } = useRecentlyViewed();

  const recentlyViewedProducts = mapIdsToProducts(recentlyViewedIds).slice(0, 4);
  const seedIds = [...favoriteIds, ...recentlyViewedIds];
  const seedProducts = mapIdsToProducts(seedIds);
  const seedCategories = new Set(seedProducts.map((product) => product.category));

  const recommendedProducts = products
    .filter((product) => seedCategories.has(product.category) && !seedIds.includes(product.id))
    .sort((a, b) => b.aiScore - a.aiScore)
    .slice(0, 4);

  return (
    <>
      {recentlyViewedProducts.length > 0 ? (
        <section className="mt-16">
          <div className="mb-6">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 md:text-4xl">Recently Viewed</h2>
            <p className="mt-2 text-gray-500">Quick access to products you checked recently.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            {recentlyViewedProducts.map((product) => (
              <ProductCard key={`recent-${product.id}`} product={product} highlightLabel="Recent" />
            ))}
          </div>
        </section>
      ) : null}

      {recommendedProducts.length > 0 ? (
        <section className="mt-16">
          <div className="mb-6">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 md:text-4xl">Recommended For You</h2>
            <p className="mt-2 text-gray-500">Based on your favorites and recently viewed categories.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            {recommendedProducts.map((product) => (
              <ProductCard key={`recommended-${product.id}`} product={product} highlightLabel="For You" />
            ))}
          </div>
        </section>
      ) : null}
    </>
  );
}
