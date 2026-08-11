import { API_BASE_URL, IS_STATIC_GENERATION_BUILD } from "@/services/api";
import { getAiTools } from "@/services/ai-tools.service";
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

function buildCategoryShowcase(categoryCounts: Map<string, number>): HomeCategoryCard[] {
  return HOMEPAGE_CATEGORY_CONFIG.map((entry) => {
    const productCount = categoryCounts.get(entry.id) ?? 0;

    return {
      ...entry,
      productCount,
      productCountText: productCount > 0 ? `${productCount} tools indexed` : "Ready for content",
    };
  });
}

function buildFeaturedBrandsFromTools(params: {
  provider: string;
  category: string;
}[]): HomeFeaturedBrand[] {
  const providerMap = new Map<string, { count: number; category: string }>();

  for (const item of params) {
    const existing = providerMap.get(item.provider);
    if (existing) {
      existing.count += 1;
      continue;
    }

    providerMap.set(item.provider, {
      count: 1,
      category: item.category,
    });
  }

  return Array.from(providerMap.entries())
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
  const fallback: HomeGuideSummary[] = [
    { slug: "highlevel-pricing", title: "HighLevel Pricing: Plans, Features & What You Should Know", excerpt: "A clear breakdown of HighLevel plans for agencies and businesses.", category: "guide" },
    { slug: "beehiiv-pricing", title: "beehiiv Pricing: Plans, Features & Newsletter Costs", excerpt: "beehiiv plans for creators — Launch, Scale, and Max explained.", category: "guide" },
    { slug: "moosend-pricing", title: "Moosend Pricing: Plans, Features & Who It Is For", excerpt: "Moosend email marketing plans and subscriber-based pricing.", category: "guide" },
    { slug: "beehiiv-vs-substack", title: "beehiiv vs Substack: Which Newsletter Platform Is Right for You?", excerpt: "Side-by-side comparison of monetization, growth, and publishing features.", category: "comparison" },
  ];

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
  const [toolsResponse, guides] = await Promise.all([getAiTools(), getLatestGuides(4)]);

  const categoryCounts = new Map<string, number>();
  for (const tool of toolsResponse.items) {
    const current = categoryCounts.get(tool.category.slug) ?? 0;
    categoryCounts.set(tool.category.slug, current + 1);
  }

  const toolProviderRows = toolsResponse.items.map((tool) => ({
    provider: tool.provider,
    category: tool.category.name,
  }));

  // Surface affiliate tools on homepage
  const FEATURED_SLUGS = ["elevenlabs", "highlevel", "moosend", "beehiiv", "synthesia"];
  const featuredTools = FEATURED_SLUGS
    .map((slug) => toolsResponse.items.find((t) => t.slug === slug))
    .filter((t): t is AITool => t !== undefined);

  return {
    "categories.showcase": buildCategoryShowcase(categoryCounts),
    "trust.default": HOMEPAGE_TRUST_SIGNALS,
    "comparisons.popular": HOMEPAGE_POPULAR_COMPARISONS,
    "guides.latest": guides,
    "tools.featured": featuredTools,
    "products.trending": [],
    "products.featured": [],
    "products.newArrivals": [],
    "brands.featured": buildFeaturedBrandsFromTools(toolProviderRows),
    "searches.trending": HOMEPAGE_TRENDING_SEARCHES,
  };
}
