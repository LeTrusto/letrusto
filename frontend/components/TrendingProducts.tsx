import ProductCard from "./ProductCard";
import { getCatalogMetadata, getHomeCollections } from "@/services/product.service";

export default async function TrendingProducts() {
  const [{ trending }, metadata] = await Promise.all([
    getHomeCollections(),
    getCatalogMetadata(),
  ]);

  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-6">

        <h2 className="text-4xl font-bold text-center mb-3">
          🔥 Trending Products
        </h2>

        <p className="text-center text-gray-500 mb-12">
          Most searched products today
        </p>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {trending.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              highlightLabel={metadata.productSpotlightBadges[product.id]}
            />
          ))}
        </div>

      </div>
    </section>
  );
}