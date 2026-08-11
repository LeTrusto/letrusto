import { AI_TOOLS_PUBLIC_CATEGORIES } from "@/config/aiTools";

export type HomeSectionComponent =
  | "hero"
  | "categoryShowcase"
  | "trustSignals"
  | "comparisons"
  | "guides"
  | "featuredTools"
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
    id: "intent-aware-guidance",
    title: "Intent-Aware Guidance",
    description: "Recommendations adapt to budget, workflow, and team context instead of generic top-ten lists.",
  },
  {
    id: "clear-comparisons",
    title: "Clear Comparisons",
    description: "Every comparison highlights software trade-offs that matter in real usage, not just feature checklists.",
  },
  {
    id: "editorial-context",
    title: "Editorial Context",
    description: "Buying guides, tool rationale, and plain-language summaries help teams choose with confidence.",
  },
  {
    id: "transparent-affiliates",
    title: "Transparent Affiliates",
    description: "Affiliate relationships support the platform without changing how products are evaluated or ranked.",
  },
  {
    id: "trust-by-design",
    title: "Trust by Design",
    description: "Fast pages, clean information architecture, and explainable recommendations reduce friction before purchase.",
  },
];

export const HOMEPAGE_POPULAR_COMPARISONS: HomepageComparisonItem[] = [
  {
    id: "assistant-comparison",
    title: "AI Assistant Comparison",
    subtitle: "Reasoning quality, workflow speed, and reliability for daily work.",
    href: "/compare",
    accent: "from-blue-600 to-violet-600",
  },
  {
    id: "writing-comparison",
    title: "AI Writing Tool Comparison",
    subtitle: "Draft quality, editing control, and team collaboration fit.",
    href: "/compare",
    accent: "from-indigo-600 to-cyan-600",
  },
  {
    id: "coding-comparison",
    title: "AI Coding Tool Comparison",
    subtitle: "Code assistance depth, review quality, and developer ergonomics.",
    href: "/compare",
    accent: "from-fuchsia-600 to-rose-600",
  },
];

export const HOMEPAGE_TRENDING_SEARCHES: HomeTrendingSearch[] = [
  {
    label: "Best AI assistant for startups",
    href: "/search?q=Best%20AI%20assistant%20for%20startups",
    note: "Speed and reliability",
  },
  {
    label: "AI writing tool for SEO",
    href: "/search?q=AI%20writing%20tool%20for%20SEO",
    note: "Content operations",
  },
  {
    label: "Best AI tool for coding",
    href: "/search?q=Best%20AI%20tool%20for%20coding",
    note: "Developer productivity",
  },
  {
    label: "AI video tool for creators",
    href: "/search?q=AI%20video%20tool%20for%20creators",
    note: "Video workflows",
  },
  {
    label: "AI image design tool for marketing",
    href: "/search?q=AI%20image%20design%20tool%20for%20marketing",
    note: "Creative output",
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
    title: "AI Tool Categories",
    subtitle: "Explore tool categories with trusted research, comparisons, and practical buying context.",
  },
  {
    id: "featured-tools",
    enabled: true,
    order: 3,
    component: "featuredTools",
    dataSource: "tools.featured",
    title: "Featured AI Tools",
    subtitle: "Explore tools we've researched and selected for specific workflows.",
  },
  {
    id: "trust-letrusto",
    enabled: true,
    order: 4,
    component: "trustSignals",
    dataSource: "trust.default",
    title: "Why Trust LeTrusto",
    subtitle: "Research, comparisons, and recommendation logic designed to make buying decisions clearer and faster.",
  },
  {
    id: "ai-comparisons",
    enabled: true,
    order: 5,
    component: "comparisons",
    dataSource: "comparisons.popular",
    title: "AI Comparison Starting Points",
    subtitle: "Evaluate options with practical trade-offs before you commit budget.",
    ctaLabel: "Open Compare",
    ctaHref: "/compare",
  },
  {
    id: "ai-guides",
    enabled: true,
    order: 6,
    component: "guides",
    dataSource: "guides.latest",
    title: "AI Buying Guides",
    subtitle: "Research-backed guidance for choosing software with confidence.",
    ctaLabel: "View all guides",
    ctaHref: "/guides",
  },
  {
    id: "trending-searches",
    enabled: true,
    order: 7,
    component: "trendingSearches",
    dataSource: "searches.trending",
    title: "Popular AI Tool Searches",
    subtitle: "Jump into common starting points teams use when narrowing AI software options.",
  },
  {
    id: "newsletter",
    enabled: true,
    order: 8,
    component: "newsletter",
    dataSource: "none",
    title: "Get AI Tool Buying Updates",
    subtitle: "Receive occasional research notes, comparison updates, and new buying guides.",
  },
];
