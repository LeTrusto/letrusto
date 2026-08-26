import type { AITool } from "@/types/ai-tools";
import {
  HOMEPAGE_TRENDING_SEARCHES,
  HOMEPAGE_CATEGORY_CONFIG,
  HOMEPAGE_POPULAR_COMPARISONS,
  HOMEPAGE_TRUST_SIGNALS,
  type HomeFeaturedBrand,
  type HomeTrendingSearch,
  type HomepageCategoryConfig,
  type HomepageComparisonItem,
  type TrustSignal,
} from "@/config/homepage";
import type { Product } from "@/types/products";

export type HomeCategoryCard = HomepageCategoryConfig & {
  productCount: number;
  productCountText: string;
};

export type HomeGuideSummary = {
  slug: string;
  title: string;
  excerpt: string;
  category: string;
};

export type HomeProductRailItem = Product;

export type HomepageDataSources = {
  "categories.showcase": HomeCategoryCard[];
  "trust.default": TrustSignal[];
  "comparisons.popular": HomepageComparisonItem[];
  "guides.latest": HomeGuideSummary[];
  "tools.featured": AITool[];
  "products.trending": HomeProductRailItem[];
  "products.featured": HomeProductRailItem[];
  "products.newArrivals": HomeProductRailItem[];
  "brands.featured": HomeFeaturedBrand[];
  "searches.trending": HomeTrendingSearch[];
};

function buildCategoryShowcase(): HomeCategoryCard[] {
  return HOMEPAGE_CATEGORY_CONFIG.map((entry) => ({
    ...entry,
    productCount: 0,
    productCountText: "Coming soon",
  }));
}

export async function getHomepageDataSources(): Promise<HomepageDataSources> {
  return {
    "categories.showcase": buildCategoryShowcase(),
    "trust.default": HOMEPAGE_TRUST_SIGNALS,
    "comparisons.popular": HOMEPAGE_POPULAR_COMPARISONS,
    "guides.latest": [],
    "tools.featured": [],
    "products.trending": [],
    "products.featured": [],
    "products.newArrivals": [],
    "brands.featured": [],
    "searches.trending": HOMEPAGE_TRENDING_SEARCHES,
  };
}
