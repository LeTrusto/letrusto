import ProductCard from "./ProductCard";
import { productSpotlightBadges, products } from "../lib/products";

export default function TrendingProducts() {
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
          {products.slice(0, 8).map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              highlightLabel={productSpotlightBadges[product.id]}
            />
          ))}
        </div>

      </div>
    </section>
  );
}