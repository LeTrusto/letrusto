import { API_BASE_URL, IS_STATIC_GENERATION_BUILD } from "@/services/api";
import { getAllProducts, type Product } from "@/services/product.service";
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
  "products.trending": HomeProductRailItem[];
  "products.featured": HomeProductRailItem[];
  "products.newArrivals": HomeProductRailItem[];
  "brands.featured": HomeFeaturedBrand[];
  "searches.trending": HomeTrendingSearch[];
};

const CATEGORY_MATCH_RE = /[^a-z0-9-]/g;

function normalize(text: string) {
  return text.toLowerCase().replace(CATEGORY_MATCH_RE, "");
}

function includesHint(source: string, hint: string) {
  const sourceNorm = normalize(source);
  const hintNorm = normalize(hint);
  return sourceNorm.includes(hintNorm);
}

function resolveCategoryCount(items: Product[], hints: string[]) {
  return items.filter((product) => {
    const source = [product.category, product.parentCategory, product.name, product.tags?.join(" ")]
      .filter(Boolean)
      .join(" ");

    return hints.some((hint) => includesHint(source, hint));
  }).length;
}

function buildCategoryShowcase(allProducts: Product[]): HomeCategoryCard[] {
  return HOMEPAGE_CATEGORY_CONFIG.map((entry) => {
    const productCount = resolveCategoryCount(allProducts, entry.categoryHints);

    return {
      ...entry,
      productCount,
      productCountText: productCount > 0 ? `${productCount} tools indexed` : "Ready for content",
    };
  });
}

function buildFeaturedBrands(allProducts: Product[]): HomeFeaturedBrand[] {
  const brandMap = new Map<string, { count: number; category: string }>();

  for (const product of allProducts) {
    const existing = brandMap.get(product.brand);
    if (existing) {
      existing.count += 1;
      continue;
    }

    brandMap.set(product.brand, {
      count: 1,
      category: product.category,
    });
  }

  return Array.from(brandMap.entries())
    .sort((left, right) => right[1].count - left[1].count)
    .slice(0, 8)
    .map(([name, info]) => ({
      name,
      category: info.category,
      href: `/search?brand=${encodeURIComponent(name)}`,
      note: `${info.count} product${info.count === 1 ? "" : "s"} in catalog`,
    }));
}

const AI_GUIDE_KEYWORDS = [
  "ai",
  "tool",
  "assistant",
  "software",
  "saas",
  "automation",
  "writing",
  "design",
  "video",
  "audio",
  "coding",
  "developer",
  "workflow",
  "productivity",
];

function isAiGuide(item: HomeGuideSummary) {
  const haystack = `${item.title} ${item.excerpt} ${item.slug} ${item.category}`.toLowerCase();
  return AI_GUIDE_KEYWORDS.some((keyword) => haystack.includes(keyword));
}

async function getLatestGuides(limit: number): Promise<HomeGuideSummary[]> {
  const fallback: HomeGuideSummary[] = [];

  if (IS_STATIC_GENERATION_BUILD) {
    return fallback.slice(0, limit);
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 4000);

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/articles?page_size=${limit}`, {
      signal: controller.signal,
      next: { revalidate: 300 },
    });

    if (!response.ok) {
      return fallback.slice(0, limit);
    }

    const body = (await response.json()) as { items?: HomeGuideSummary[] };
    return (body.items ?? fallback).filter(isAiGuide).slice(0, limit);
  } catch {
    return fallback.slice(0, limit);
  } finally {
    clearTimeout(timeout);
  }
}

export async function getHomepageDataSources(): Promise<HomepageDataSources> {
  const [allProducts, guides, collections] = await Promise.all([
    getAllProducts(),
    getLatestGuides(4),
    import("@/services/product.service").then(({ getHomeCollections }) => getHomeCollections()),
  ]);

  return {
    "categories.showcase": buildCategoryShowcase(allProducts),
    "trust.default": HOMEPAGE_TRUST_SIGNALS,
    "comparisons.popular": HOMEPAGE_POPULAR_COMPARISONS,
    "guides.latest": guides,
    "products.trending": collections.trending.slice(0, 4),
    "products.featured": collections.featured.slice(0, 4),
    "products.newArrivals": collections.newArrivals.slice(0, 4),
    "brands.featured": buildFeaturedBrands(allProducts),
    "searches.trending": HOMEPAGE_TRENDING_SEARCHES,
  };
}
