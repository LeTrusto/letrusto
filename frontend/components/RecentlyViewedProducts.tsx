"use client";

import ProductCard from "@/components/ProductCard";
import { useRecentlyViewed } from "@/hooks/useRecentlyViewed";
import { products } from "@/lib/products";

type RecentlyViewedProductsProps = {
  currentProductId: string;
};

export default function RecentlyViewedProducts({
  currentProductId,
}: RecentlyViewedProductsProps) {
  const { recentlyViewedIds } = useRecentlyViewed(currentProductId);

  const recentlyViewedProducts = recentlyViewedIds
    .filter((productId) => productId !== currentProductId)
    .map((productId) => products.find((product) => product.id === productId))
    .filter((product): product is (typeof products)[number] => Boolean(product));

  if (recentlyViewedProducts.length === 0) {
    return null;
  }

  return (
    <section className="mt-16 space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Recently Viewed</h2>
        <p className="mt-2 text-gray-500">Pick up where you left off with products you opened recently.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {recentlyViewedProducts.map((product) => (
          <ProductCard key={product.id} product={product} compareWithId={currentProductId} />
        ))}
      </div>
    </section>
  );
}
