import type {
  PaginatedProductsResponse,
  Product,
  ProductAiScoreFilter,
  ProductFilterState,
  ProductPriceFilter,
  ProductQueryOptions,
  ProductRatingFilter,
  ProductSortOption,
} from "@/types/products";
import { apiRequest, buildQueryString } from "@/services/api";
import type { CommerceCategory, CommerceProduct } from "@/types/commerce";

const CATEGORY_ALIASES: Record<string, string> = {
  smartphones: "phone",
  phone: "phone",
  "laptops-ultrabooks": "laptop",
  "tablets-ipads": "tablet",
  "smartwatches-bands": "smartwatch",
  "digital-cameras": "camera",
  "televisions-oleds": "television",
};

function toNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return 0;
}

function normalizeProduct(product: Product): Product {
  return {
    ...product,
    priceValue: toNumber(product.priceValue),
    rating: toNumber(product.rating),
    aiScore: toNumber(product.aiScore),
    priceHistory: product.priceHistory.map((point) => ({ ...point, price: toNumber(point.price) })),
    reviews: product.reviews.map((review) => ({ ...review, rating: toNumber(review.rating) })),
  };
}

function normalizeCategoryValue(value: ProductQueryOptions["category"]) {
  if (!value || value === "all") return value;
  const raw = String(value).trim().toLowerCase();
  return (CATEGORY_ALIASES[raw] ?? raw) as ProductFilterState["category"];
}

function normalizeQueryOptions(options: ProductQueryOptions): ProductQueryOptions {
  return { ...options, category: normalizeCategoryValue(options.category) };
}

export async function getAllProducts() {
  const catalog = await apiRequest<Product[]>("/products");
  return catalog.map(normalizeProduct);
}

export async function getPublicProducts() {
  return getAllProducts();
}

export async function getProductById(productId: string) {
  try {
    return normalizeProduct(await apiRequest<Product>(`/products/${encodeURIComponent(productId)}`));
  } catch {
    return null;
  }
}

export async function getPublicProduct(productId: string) {
  return normalizeProduct(await apiRequest<Product>(`/products/${encodeURIComponent(productId)}`));
}

const COMMERCE_CATEGORIES = new Set<CommerceCategory>(["apparel", "wall-art", "accessories", "home-living", "stationery"]);

function categoryLabel(slug: string) {
  return slug.split("-").map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
}

export function toCommerceProduct(product: Product): CommerceProduct {
  const variants = product.variants ?? [];
  const category = COMMERCE_CATEGORIES.has(product.category as CommerceCategory)
    ? product.category as CommerceCategory
    : product.parentCategory && COMMERCE_CATEGORIES.has(product.parentCategory as CommerceCategory)
      ? product.parentCategory as CommerceCategory
      : product.category;

  return {
    id: product.id,
    slug: product.id,
    name: product.name,
    description: product.description,
    price: product.priceValue,
    currency: "INR",
    images: product.images.length > 0 ? product.images : ["/images/products/placeholder.svg"],
    category,
    categoryLabel: categoryLabel(product.category),
    catalogVariants: variants.map((variant) => ({ id: variant.id, label: variant.label, price: variant.priceValue, available: variant.available, inventory: variant.inventory })),
    availability: variants.some((variant) => variant.available) ? "in-stock" : "out-of-stock",
    tags: product.tags,
    specs: product.specs,
    estimatedDelivery: "Delivery calculated at checkout",
    returnInfo: "Returns subject to product policy",
  };
}

export async function getProductsByIds(productIds: string[]) {
  const catalog = await apiRequest<Product[]>(`/products${buildQueryString({ ids: productIds.join(",") })}`);
  return catalog.map(normalizeProduct);
}

export async function getProductSearch(options: ProductQueryOptions): Promise<PaginatedProductsResponse> {
  const normalized = normalizeQueryOptions(options);
  const response = await apiRequest<PaginatedProductsResponse>(`/products/search${buildQueryString({
    q: normalized.q,
    sort: normalized.sortBy,
    category: normalized.category,
    subcategory: normalized.subcategory,
    series: normalized.series,
    price: normalized.price,
    rating: normalized.rating,
    aiScore: normalized.aiScore,
    brand: normalized.brand,
    minPrice: normalized.minPrice,
    maxPrice: normalized.maxPrice,
    minRating: normalized.minRating,
    minAiScore: normalized.minAiScore,
    page: normalized.page,
    pageSize: normalized.pageSize,
  })}`);
  return { ...response, items: response.items.map(normalizeProduct) };
}

export async function getAiRecommendations(query: string, limit = 4) {
  const recommendations = await apiRequest<Product[]>(`/products/recommendations${buildQueryString({ q: query.trim(), limit: Math.max(1, limit) })}`);
  return recommendations.map(normalizeProduct);
}

export async function getRelatedProductsByProductId(productId: string, limit = 4) {
  const related = await apiRequest<Product[]>(`/products/${encodeURIComponent(productId)}/similar${buildQueryString({ limit: Math.max(1, limit) })}`);
  return related.map(normalizeProduct);
}

export async function getCompareProducts(firstId?: string, secondId?: string) {
  const response = await apiRequest<{ firstProduct: Product; secondProduct: Product }>(`/products/compare${buildQueryString({ first: firstId, second: secondId })}`);
  return { firstProduct: normalizeProduct(response.firstProduct), secondProduct: normalizeProduct(response.secondProduct) };
}

export async function getSearchSuggestions(limit = 24) {
  return apiRequest<string[]>(`/products/suggestions${buildQueryString({ limit: Math.max(1, limit) })}`);
}

export async function getHomeCollections() {
  const collections = await apiRequest<{ featured: Product[]; newArrivals: Product[]; topAiPicks: Product[]; trending: Product[] }>("/products/collections/home");
  return {
    featured: collections.featured.map(normalizeProduct),
    newArrivals: collections.newArrivals.map(normalizeProduct),
    topAiPicks: collections.topAiPicks.map(normalizeProduct),
    trending: collections.trending.map(normalizeProduct),
  };
}

export async function getCatalogMetadata() {
  return apiRequest<{ categoryLabels: Record<string, string>; categoryPluralLabels: Record<string, string>; productSpotlightBadges: Record<string, string>; brands: string[] }>("/products/metadata");
}

export function getCompareHref(productId: string, compareWithId?: string) {
  return `/compare?first=${encodeURIComponent(productId)}${compareWithId ? `&second=${encodeURIComponent(compareWithId)}` : ""}`;
}

export type {
  Product,
  ProductAiScoreFilter,
  ProductFilterState,
  ProductPriceFilter,
  ProductQueryOptions,
  ProductRatingFilter,
  ProductSortOption,
};
