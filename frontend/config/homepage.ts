import { AI_TOOLS_PUBLIC_CATEGORIES } from "@/config/aiTools";

export type HomeSectionComponent =
  | "hero"
  | "categoryShowcase"
  | "trustSignals"
  | "comparisons"
  | "guides"
  | "featuredTools"
  | "askLeTrusto"
  | "productRail"
  | "featuredBrands"
  | "trendingSearches"
  | "newsletter";

export type HomeDataSourceKey =
  | "none"
  | "categories.showcase"
  | "trust.default"
  | "comparisons.popular"
  | "guides.latest"
  | "tools.featured"
  | "products.trending"
  | "products.featured"
  | "products.newArrivals"
  | "brands.featured"
  | "searches.trending";

export type HomepageSectionConfig = {
  id: string;
  enabled: boolean;
  order: number;
  component: HomeSectionComponent;
  dataSource: HomeDataSourceKey;
  title?: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
  maxItems?: number;
  highlightLabel?: string;
};

export type HomepageCategoryConfig = {
  id: string;
  name: string;
  description: string;
  href: string;
  eyebrow: string;
  featuredBullets: string[];
  categoryHints: string[];
};

export type TrustSignal = {
  id: string;
  title: string;
  description: string;
};

export type HomepageComparisonItem = {
  id: string;
  title: string;
  subtitle: string;
  href: string;
  accent: string;
};

export type HomeFeaturedBrand = {
  name: string;
  category: string;
  href: string;
  note: string;
};

export type HomeTrendingSearch = {
  label: string;
  href: string;
  note: string;
};

export const HOMEPAGE_CATEGORY_CONFIG: HomepageCategoryConfig[] = AI_TOOLS_PUBLIC_CATEGORIES.map((category) => ({
  id: category.id,
  name: category.name,
  description: category.description,
  href: category.href,
  eyebrow: category.eyebrow,
  featuredBullets: category.featuredBullets,
  categoryHints: category.categoryHints,
}));

export const HOMEPAGE_TRUST_SIGNALS: TrustSignal[] = [
  {
    id: "printed-fresh",
    title: "Printed Fresh",
    description: "Every product is printed on demand — no mass production, no warehouse stock, just your design made fresh.",
  },
  {
    id: "global-shipping",
    title: "Global Shipping",
    description: "We ship to 30+ countries from local production facilities so your order arrives fast.",
  },
  {
    id: "quality-guaranteed",
    title: "Quality Guaranteed",
    description: "Premium materials, vibrant prints, and free replacements if anything arrives less than perfect.",
  },
  {
    id: "unique-designs",
    title: "Unique Designs",
    description: "Original artwork you won't find anywhere else — curated collections refreshed regularly.",
  },
  {
    id: "easy-returns",
    title: "Easy Returns",
    description: "Not happy? We handle replacements and refunds without hassle.",
  },
];

export const HOMEPAGE_POPULAR_COMPARISONS: HomepageComparisonItem[] = [];

export const HOMEPAGE_TRENDING_SEARCHES: HomeTrendingSearch[] = [
  {
    label: "Custom t-shirts",
    href: "/shop?category=apparel",
    note: "Most popular",
  },
  {
    label: "Wall art prints",
    href: "/shop?category=wall-art",
    note: "Trending",
  },
  {
    label: "Custom mugs",
    href: "/shop?category=home-living",
    note: "Gift idea",
  },
  {
    label: "Phone cases",
    href: "/shop?category=accessories",
    note: "New designs",
  },
];

export const HOMEPAGE_SECTIONS: HomepageSectionConfig[] = [
  {
    id: "hero",
    enabled: true,
    order: 1,
    component: "hero",
    dataSource: "none",
  },
  {
    id: "categories",
    enabled: true,
    order: 2,
    component: "categoryShowcase",
    dataSource: "categories.showcase",
    title: "Shop by Category",
    subtitle: "Custom printed products shipped worldwide.",
  },
  {
    id: "trust-letrusto",
    enabled: true,
    order: 3,
    component: "trustSignals",
    dataSource: "trust.default",
    title: "Why LeTrusto",
    subtitle: "Fresh prints, global shipping, and quality you can trust.",
  },
  {
    id: "trending-searches",
    enabled: true,
    order: 4,
    component: "trendingSearches",
    dataSource: "searches.trending",
    title: "Popular Right Now",
    subtitle: "Trending products our customers love.",
  },
  {
    id: "newsletter",
    enabled: true,
    order: 5,
    component: "newsletter",
    dataSource: "none",
    title: "Get New Design Drops",
    subtitle: "Be the first to see new collections and limited-edition prints.",
  },
];
