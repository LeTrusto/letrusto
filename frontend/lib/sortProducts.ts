import type { Product, ProductSortOption } from "@/types/products";

import { scoreProductForQuery } from "@/lib/recommendations";

export function sortProducts(products: Product[], sortBy: ProductSortOption, query = "") {
  const sorted = [...products];

  switch (sortBy) {
    case "price-low":
      return sorted.sort((left, right) => left.priceValue - right.priceValue);
    case "price-high":
      return sorted.sort((left, right) => right.priceValue - left.priceValue);
    case "rating-high":
      return sorted.sort((left, right) => right.rating - left.rating);
    case "ai-high":
      return sorted.sort((left, right) => right.aiScore - left.aiScore);
    case "relevance":
    default:
      return sorted.sort((left, right) => {
        const scoreDelta = scoreProductForQuery(right, query) - scoreProductForQuery(left, query);

        if (scoreDelta !== 0) {
          return scoreDelta;
        }

        return right.aiScore - left.aiScore;
      });
  }
}
