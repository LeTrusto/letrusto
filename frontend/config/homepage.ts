export type HomeSectionComponent =
  | "hero"
  | "categoryShowcase"
  | "productGrid"
  | "productRail"
  | "aiFeatured"
  | "dealsSpotlight"
  | "comingSoonRoadmap"
  | "trustSignals"
  | "guides"
  | "askAiCta";

export type HomeDataSourceKey =
  | "none"
  | "categories.showcase"
  | "products.trending"
  | "products.newArrivals"
  | "products.aiPicks"
  | "products.bestDeals"
  | "comingSoon.verticals"
  | "guides.latest"
  | "trust.default";

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
  image: string;
  gradientClass: string;
  categoryHints: string[];
  fallbackCount: string;
};

export type TrustSignal = {
  id: string;
  title: string;
  description: string;
};

export const HOMEPAGE_CATEGORY_CONFIG: HomepageCategoryConfig[] = [
  {
    id: "electronics",
    name: "Electronics",
    description: "Phones, laptops, TVs, wearables, and more.",
    href: "/category/electronics",
    image: "/images/products/iphone16pro-1.svg",
    gradientClass: "from-indigo-700/80 to-fuchsia-600/80",
    categoryHints: ["phone", "laptop", "tablet", "camera", "television", "gaming", "headphones", "smartwatch"],
    fallbackCount: "120+",
  },
  {
    id: "hosting",
    name: "Hosting",
    description: "Shared, managed, and cloud hosting recommendations.",
    href: "/category/hosting",
    image: "/images/products/macbook-air-m4.png",
    gradientClass: "from-cyan-700/80 to-blue-700/80",
    categoryHints: ["hosting", "web-hosting", "cloud", "server"],
    fallbackCount: "40+",
  },
  {
    id: "saas",
    name: "SaaS Tools",
    description: "Business software, productivity, and AI tools.",
    href: "/category/saas",
    image: "/images/products/lenovo-legion-go-1.jpg",
    gradientClass: "from-emerald-700/80 to-teal-600/80",
    categoryHints: ["saas", "software", "productivity", "automation"],
    fallbackCount: "60+",
  },
  {
    id: "pet-care",
    name: "Pet Care",
    description: "Smart picks for pet health, food, and grooming.",
    href: "/category/pet-care",
    image: "/images/products/sony-wh1000xm6.png",
    gradientClass: "from-amber-700/80 to-orange-600/80",
    categoryHints: ["pet-care"],
    fallbackCount: "25+",
  },
  {
    id: "beauty",
    name: "Beauty",
    description: "Skincare, grooming, and wellness essentials.",
    href: "/category/beauty",
    image: "/images/products/sony-a7-iv-1.jpg",
    gradientClass: "from-rose-700/80 to-pink-600/80",
    categoryHints: ["beauty"],
    fallbackCount: "35+",
  },
  {
    id: "home",
    name: "Home",
    description: "Kitchen, appliances, and everyday home upgrades.",
    href: "/category/home-kitchen",
    image: "/images/products/ifb-senator-mxn-8012-1.jpg",
    gradientClass: "from-violet-700/80 to-indigo-600/80",
    categoryHints: ["home-kitchen", "refrigerator", "washing-machine", "furniture"],
    fallbackCount: "55+",
  },
  {
    id: "gaming",
    name: "Gaming",
    description: "Consoles, accessories, and performance gear.",
    href: "/category/gaming",
    image: "/images/products/nintendo-switch-oled-1.png",
    gradientClass: "from-red-700/80 to-orange-600/80",
    categoryHints: ["gaming"],
    fallbackCount: "30+",
  },
  {
    id: "fitness",
    name: "Fitness",
    description: "Wearables and training essentials for active lifestyles.",
    href: "/category/fitness",
    image: "/images/products/samsung-galaxy-tab-s10-1.png",
    gradientClass: "from-lime-700/80 to-emerald-600/80",
    categoryHints: ["fitness"],
    fallbackCount: "20+",
  },
  {
    id: "kitchen",
    name: "Kitchen",
    description: "Appliances and tools for smarter cooking.",
    href: "/category/kitchen",
    image: "/images/products/whirlpool-stainwash-pro-9kg-1.jpg",
    gradientClass: "from-sky-700/80 to-cyan-600/80",
    categoryHints: ["kitchen"],
    fallbackCount: "45+",
  },
];

export const HOMEPAGE_TRUST_SIGNALS: TrustSignal[] = [
  {
    id: "ai-recommendations",
    title: "AI Recommendations",
    description: "Intent-aware suggestions tuned to your budget, use case, and priorities.",
  },
  {
    id: "verified-reviews",
    title: "Verified Reviews",
    description: "Signals from real buyer sentiment and long-term ownership feedback.",
  },
  {
    id: "comparisons",
    title: "Smart Comparisons",
    description: "Side-by-side product breakdowns to surface meaningful differences quickly.",
  },
  {
    id: "buying-guides",
    title: "Buying Guides",
    description: "Expert research that converts complexity into clear decisions.",
  },
  {
    id: "best-deals",
    title: "Best Deals",
    description: "Track value and spot opportunities without noisy price chasing.",
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
    title: "Browse Categories",
    subtitle: "Explore fast-growing verticals with AI-curated picks and trusted comparisons.",
  },
  {
    id: "trending-now",
    enabled: true,
    order: 3,
    component: "productGrid",
    dataSource: "products.trending",
    title: "Trending Now",
    subtitle: "High-momentum products across categories buyers are actively researching.",
    ctaLabel: "See all products",
    ctaHref: "/search",
    maxItems: 8,
    highlightLabel: "Trending",
  },
  {
    id: "new-arrivals",
    enabled: true,
    order: 4,
    component: "productRail",
    dataSource: "products.newArrivals",
    title: "New Arrivals",
    subtitle: "Fresh launches and newly listed products, optimized for quick discovery.",
    ctaLabel: "Browse new products",
    ctaHref: "/search?sort=relevance",
    maxItems: 10,
    highlightLabel: "New",
  },
  {
    id: "trust-letrusto",
    enabled: true,
    order: 5,
    component: "trustSignals",
    dataSource: "trust.default",
    title: "Why Trust LeTrusto?",
    subtitle: "The AI-first workflow that helps you choose with confidence.",
  },
  {
    id: "hosting-saas",
    enabled: true,
    order: 6,
    component: "comingSoonRoadmap",
    dataSource: "comingSoon.verticals",
    title: "Hosting & SaaS",
    subtitle: "Premium advisor experiences for cloud, software, and service buying are launching next.",
    ctaLabel: "Explore Hosting & SaaS",
    ctaHref: "/category/hosting",
    maxItems: 4,
  },
  {
    id: "ai-picks",
    enabled: true,
    order: 7,
    component: "aiFeatured",
    dataSource: "products.aiPicks",
    title: "AI Picks",
    subtitle: "The strongest quality-to-value picks ranked by LeTrusto AI.",
    ctaLabel: "Ask AI for your pick",
    ctaHref: "/ai",
    maxItems: 4,
    highlightLabel: "AI Pick",
  },
  {
    id: "best-deals",
    enabled: true,
    order: 8,
    component: "dealsSpotlight",
    dataSource: "products.bestDeals",
    title: "Best Deals",
    subtitle: "High-value picks balancing price, reliability, and long-term utility.",
    ctaLabel: "View more deals",
    ctaHref: "/deals",
    maxItems: 4,
    highlightLabel: "Deal",
  },
  {
    id: "latest-guides",
    enabled: true,
    order: 9,
    component: "guides",
    dataSource: "guides.latest",
    title: "Latest Buying Guides",
    subtitle: "Editorial guidance and deep dives to help you buy smarter.",
    ctaLabel: "All guides",
    ctaHref: "/guides",
    maxItems: 4,
  },
  {
    id: "ask-ai-cta",
    enabled: true,
    order: 10,
    component: "askAiCta",
    dataSource: "none",
    title: "Still Deciding? Ask LeTrusto AI",
    subtitle: "Share your budget and priorities to get a personalized shortlist in seconds.",
    ctaLabel: "Ask AI Now",
    ctaHref: "/ai",
  },
];
