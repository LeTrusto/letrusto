export type ProductCategory =
  | "phone"
  | "laptop"
  | "headphones"
  | "smartwatch"
  | "television"
  | "refrigerator"
  | "washing-machine"
  | "gaming"
  | "tablet"
  | "camera";

export type ProductAvailability = "In Stock" | "Limited Stock" | "Pre-order";

export type ProductSpecification = {
  label: string;
  value: string;
};

export type ProductPriceHistoryPoint = {
  label: string;
  price: number;
};

export type ProductReview = {
  author: string;
  title: string;
  rating: number;
  comment: string;
  date: string;
};

export type ProductBuyLink = {
  label: "Amazon" | "Flipkart" | "Croma" | "Reliance Digital";
  href: string;
};

export type Product = {
  id: string;
  name: string;
  brand: string;
  price: string;
  priceValue: number;
  image: string;
  images: string[];
  fallbackImage: string;
  category: ProductCategory;
  availability: ProductAvailability;
  description: string;
  features: string[];
  aiScore: number;
  rating: number;
  specs: ProductSpecification[];
  pros: string[];
  cons: string[];
  aiSummary: string;
  bestFor: string[];
  notRecommendedFor: string[];
  tags: string[];
  priceHistory: ProductPriceHistoryPoint[];
  reviews: ProductReview[];
  reviewSummary: string;
  buyLinks: ProductBuyLink[];
  similarProductIds: string[];
};

export type ProductSortOption =
  | "relevance"
  | "price-low"
  | "price-high"
  | "rating-high"
  | "ai-high";

export type ProductPriceFilter =
  | "all"
  | "under-30000"
  | "30000-80000"
  | "above-80000";

export type ProductRatingFilter = "all" | "4-plus" | "4.5-plus";

export type ProductAiScoreFilter = "all" | "above-90";

export type ProductFilterState = {
  category: "all" | ProductCategory;
  price: ProductPriceFilter;
  rating: ProductRatingFilter;
  aiScore: ProductAiScoreFilter;
};

export type ProductPagination = {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
};

export type ProductQueryOptions = {
  q?: string;
  sortBy?: ProductSortOption;
  category?: ProductFilterState["category"];
  price?: ProductPriceFilter;
  rating?: ProductRatingFilter;
  aiScore?: ProductAiScoreFilter;
  brand?: string;
  minPrice?: number;
  maxPrice?: number;
  minRating?: number;
  minAiScore?: number;
  page?: number;
  pageSize?: number;
};

export type PaginatedProductsResponse = {
  items: Product[];
  pagination: ProductPagination;
};

