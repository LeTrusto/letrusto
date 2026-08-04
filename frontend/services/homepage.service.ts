import {
  API_BASE_URL,
  IS_STATIC_GENERATION_BUILD,
} from "@/services/api";
import {
  getAllProducts,
  getHomeCollections,
  type Product,
} from "@/services/product.service";
import {
  HOMEPAGE_CATEGORY_CONFIG,
  HOMEPAGE_TRUST_SIGNALS,
  type HomepageCategoryConfig,
  type TrustSignal,
} from "@/config/homepage";
import type { ComingSoonVertical } from "@/components/homepage/HomeComingSoonRoadmapSection";

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
  "products.trending": Product[];
  "products.newArrivals": Product[];
  "products.aiPicks": Product[];
  "products.bestDeals": Product[];
  "comingSoon.verticals": ComingSoonVertical[];
  "guides.latest": HomeGuideSummary[];
  "trust.default": TrustSignal[];
};

const CATEGORY_FALLBACK_RE = /[^a-z0-9-]/g;

function normalize(text: string) {
  return text.toLowerCase().replace(CATEGORY_FALLBACK_RE, "");
}

function includesHint(value: string, hint: string) {
  const valueNorm = normalize(value);
  const hintNorm = normalize(hint);
  return valueNorm.includes(hintNorm);
}

const COMING_SOON_VERTICALS: ComingSoonVertical[] = [
  {
    id: "hosting",
    title: "Hosting Advisor",
    subtitle: "AI-led recommendations for startups, ecommerce stores, and enterprise workloads.",
    illustration: "HOST",
    eta: "Q4 2026",
    route: "/category/hosting",
    planned: [
      "Uptime, support, and performance benchmarks",
      "Managed WordPress and VPS comparison workflows",
      "Transparent renewal cost forecasting",
    ],
  },
  {
    id: "saas",
    title: "SaaS Buying Workspace",
    subtitle: "Evaluate software like an operator with AI scoring and adoption fit analysis.",
    illustration: "SAAS",
    eta: "Q1 2027",
    route: "/category/saas",
    planned: [
      "Role-based software recommendations",
      "Total cost and integration complexity scoring",
      "Vendor reliability and roadmap signals",
    ],
  },
  {
    id: "beauty",
    title: "Beauty Intelligence",
    subtitle: "Ingredient-aware recommendations and personalized routine guidance.",
    illustration: "BEAUTY",
    eta: "Q1 2027",
    route: "/category/beauty",
    planned: [
      "Skin concern and ingredient match scoring",
      "Routine builders by season and budget",
      "Sensitive skin safe-choice filters",
    ],
  },
  {
    id: "pet-care",
    title: "Pet Care Assistant",
    subtitle: "Safer, smarter choices for food, grooming, and wellness essentials.",
    illustration: "PET",
    eta: "Q2 2027",
    route: "/category/pet-care",
    planned: [
      "Breed and age-aware recommendations",
      "Nutrition and ingredient comparison panels",
      "Vet-informed buying guide series",
    ],
  },
];

function buildBestDeals(products: Product[]) {
  return [...products]
    .sort((left, right) => {
      const leftValueScore = left.aiScore / Math.max(left.priceValue, 1);
      const rightValueScore = right.aiScore / Math.max(right.priceValue, 1);
      return rightValueScore - leftValueScore;
    })
    .slice(0, 8);
}

function pickMixedCategoryProducts(products: Product[], maxItems: number) {
  const byCategory = new Map<string, Product[]>();

  for (const product of products) {
    const category = String(product.category);
    const bucket = byCategory.get(category) ?? [];
    bucket.push(product);
    byCategory.set(category, bucket);
  }

  const selected: Product[] = [];
  const categories = Array.from(byCategory.keys());

  while (selected.length < maxItems && categories.length > 0) {
    for (let index = categories.length - 1; index >= 0; index -= 1) {
      const category = categories[index];
      const list = byCategory.get(category);
      const next = list?.shift();

      if (next) {
        selected.push(next);
      }

      if (!list || list.length === 0) {
        categories.splice(index, 1);
      }

      if (selected.length >= maxItems) {
        break;
      }
    }
  }

  return selected;
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
    const count = resolveCategoryCount(allProducts, entry.categoryHints);
    return {
      ...entry,
      productCount: count,
      productCountText: count > 0 ? `${count}+ products` : `${entry.fallbackCount} products`,
    };
  });
}

export async function getHomepageDataSources(): Promise<HomepageDataSources> {
  const [{ trending, newArrivals, topAiPicks }, allProducts, guides] = await Promise.all([
    getHomeCollections(),
    getAllProducts(),
    getLatestGuides(4),
  ]);

  const trendingMixed = pickMixedCategoryProducts(trending.length > 0 ? trending : allProducts, 8);
  const aiPicks = [...topAiPicks].filter((product) => product.aiSummary?.trim().length > 0).slice(0, 4);

  return {
    "categories.showcase": buildCategoryShowcase(allProducts),
    "products.trending": trendingMixed,
    "products.newArrivals": newArrivals,
    "products.aiPicks": aiPicks,
    "products.bestDeals": buildBestDeals(allProducts),
    "comingSoon.verticals": COMING_SOON_VERTICALS,
    "guides.latest": guides,
    "trust.default": HOMEPAGE_TRUST_SIGNALS,
  };
}
