import { API_BASE_URL, IS_STATIC_GENERATION_BUILD } from "@/services/api";
import { getAllProducts, type Product } from "@/services/product.service";
import {
  HOMEPAGE_CATEGORY_CONFIG,
  HOMEPAGE_COMING_SOON_VERTICALS,
  HOMEPAGE_POPULAR_COMPARISONS,
  HOMEPAGE_TRUST_SIGNALS,
  type HomepageCategoryConfig,
  type HomepageComingSoonItem,
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

export type HomepageDataSources = {
  "categories.showcase": HomeCategoryCard[];
  "trust.default": TrustSignal[];
  "comparisons.popular": HomepageComparisonItem[];
  "comingSoon.hostingSaas": HomepageComingSoonItem;
  "comingSoon.beauty": HomepageComingSoonItem;
  "comingSoon.petCare": HomepageComingSoonItem;
  "guides.latest": HomeGuideSummary[];
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
  const launchedCategories = new Set(["electronics"]);

  return HOMEPAGE_CATEGORY_CONFIG.map((entry) => {
    const rawCount = resolveCategoryCount(allProducts, entry.categoryHints);
    const productCount = launchedCategories.has(entry.id) ? rawCount : 0;

    return {
      ...entry,
      productCount,
      productCountText: productCount > 0 ? `${productCount} live picks` : "Coming Soon",
    };
  });
}

async function getLatestGuides(limit: number): Promise<HomeGuideSummary[]> {
  const fallback: HomeGuideSummary[] = [
    {
      slug: "best-web-hosting-india-2026",
      title: "Best Web Hosting in India 2026",
      excerpt: "Performance, uptime, pricing, and support compared for Indian buyers.",
      category: "guide",
    },
    {
      slug: "iphone-16-pro-vs-samsung-s25-ultra",
      title: "iPhone 16 Pro vs Galaxy S25 Ultra",
      excerpt: "Camera, battery, and long-term value compared side by side.",
      category: "comparison",
    },
    {
      slug: "best-phone-under-20000-india-2026",
      title: "Best Phone Under ₹20,000",
      excerpt: "Top budget picks with strong real-world performance and reliability.",
      category: "guide",
    },
    {
      slug: "hostinger-vs-bluehost-india",
      title: "Hostinger vs Bluehost India",
      excerpt: "A practical comparison for startup and SMB hosting needs.",
      category: "comparison",
    },
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
    return (body.items ?? fallback).slice(0, limit);
  } catch {
    return fallback.slice(0, limit);
  } finally {
    clearTimeout(timeout);
  }
}

export async function getHomepageDataSources(): Promise<HomepageDataSources> {
  const [allProducts, guides] = await Promise.all([getAllProducts(), getLatestGuides(4)]);

  return {
    "categories.showcase": buildCategoryShowcase(allProducts),
    "trust.default": HOMEPAGE_TRUST_SIGNALS,
    "comparisons.popular": HOMEPAGE_POPULAR_COMPARISONS,
    "comingSoon.hostingSaas": HOMEPAGE_COMING_SOON_VERTICALS.hostingSaas,
    "comingSoon.beauty": HOMEPAGE_COMING_SOON_VERTICALS.beauty,
    "comingSoon.petCare": HOMEPAGE_COMING_SOON_VERTICALS.petCare,
    "guides.latest": guides,
  };
}
