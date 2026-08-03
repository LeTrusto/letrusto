import type { Product, ProductFilterState } from "@/types/products";

export function filterProducts(products: Product[], filters: ProductFilterState) {
  return products.filter((product) => {
    if (filters.category !== "all" && product.category !== filters.category) {
      return false;
    }

    if (filters.price === "under-30000" && product.priceValue >= 30000) {
      return false;
    }

    if (
      filters.price === "30000-80000" &&
      (product.priceValue < 30000 || product.priceValue > 80000)
    ) {
      return false;
    }

    if (filters.price === "above-80000" && product.priceValue <= 80000) {
      return false;
    }

    if (filters.rating === "4-plus" && product.rating < 4) {
      return false;
    }

    if (filters.rating === "4.5-plus" && product.rating < 4.5) {
      return false;
    }

    if (filters.aiScore === "above-90" && product.aiScore <= 90) {
      return false;
    }

    return true;
  });
}
