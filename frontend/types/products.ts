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
  | "camera"
  // Phase 6.1 top-level
  | "electronics"
  | "home-kitchen"
  | "beauty"
  | "baby-care"
  | "pet-care"
  | "fitness"
  | "furniture"
  // Phase 6.1 sub-categories
  | "smartphones"
  | "laptops-ultrabooks"
  | "tablets-ipads"
  | "earbuds-tws"
  | "smartwatches-bands"
  | "digital-cameras"
  | "bluetooth-speakers"
  | "monitors-displays"
  | "televisions-oleds"
  | (string & {});  // allow future slugs without breaking type checks

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
  id?: number;
  label: string;
  href: string;
  retailer_type?: string;
  is_affiliate?: boolean;
  click_count?: number;
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
  variants?: CatalogVariant[];
  madeToOrder?: boolean;
  category: ProductCategory;
  parentCategory?: string | null;
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
  amazonAsin?: string | null;
  amazonAffiliateUrl?: string | null;
  flipkartAffiliateUrl?: string | null;
  // Phase 6.1 catalog fields
  series?: string | null;
  modelName?: string | null;
  variant?: string | null;
  storage?: string | null;
  ram?: string | null;
  color?: string | null;
};

export type CatalogVariant = {
  id: string;
  label: string;
  price: string;
  priceValue: number;
  available: boolean;
  inventory: number;
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
  subcategory?: string;
  series?: string;
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

