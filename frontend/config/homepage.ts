export type HomeSectionComponent =
  | "hero"
  | "categoryShowcase"
  | "trustSignals"
  | "comparisons"
  | "guides"
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

export const HOMEPAGE_CATEGORY_CONFIG: HomepageCategoryConfig[] = [
  {
    id: "electronics",
    name: "Electronics",
    description: "Phones, laptops, cameras, gaming, and wearables.",
    href: "/category/electronics",
    eyebrow: "Live now",
    featuredBullets: ["Phones", "Laptops", "Audio", "TV & gaming"],
    categoryHints: ["phone", "laptop", "tablet", "camera", "television", "gaming", "headphones", "smartwatch"],
  },
  {
    id: "hosting",
    name: "Hosting",
    description: "Smart recommendations for sites, startups, and growing teams.",
    href: "/category/hosting",
    eyebrow: "Research queue",
    featuredBullets: ["Shared hosting", "Cloud", "Builders", "Domain setup"],
    categoryHints: ["hosting", "web-hosting", "cloud", "server"],
  },
  {
    id: "saas",
    name: "SaaS",
    description: "Business software guidance with AI-first evaluation frameworks.",
    href: "/category/saas",
    eyebrow: "Research queue",
    featuredBullets: ["CRM", "Automation", "Analytics", "Team tools"],
    categoryHints: ["saas", "software", "productivity", "automation"],
  },
  {
    id: "beauty",
    name: "Beauty",
    description: "Evidence-led recommendations for skincare and wellness.",
    href: "/category/beauty",
    eyebrow: "Upcoming",
    featuredBullets: ["Skincare", "Hair care", "Wellness", "Everyday essentials"],
    categoryHints: ["beauty"],
  },
  {
    id: "pet-care",
    name: "Pet Care",
    description: "Trusted picks for food, health, and everyday pet essentials.",
    href: "/category/pet-care",
    eyebrow: "Upcoming",
    featuredBullets: ["Food", "Health", "Accessories", "Care basics"],
    categoryHints: ["pet-care"],
  },
  {
    id: "home",
    name: "Home",
    description: "Appliance and lifestyle buying guidance for modern homes.",
    href: "/category/home-kitchen",
    eyebrow: "Expanding",
    featuredBullets: ["Appliances", "Cleaning", "Comfort", "Organization"],
    categoryHints: ["home-kitchen", "refrigerator", "washing-machine", "furniture"],
  },
  {
    id: "kitchen",
    name: "Kitchen",
    description: "Compare cooking and prep tools with practical recommendations.",
    href: "/category/kitchen",
    eyebrow: "Upcoming",
    featuredBullets: ["Cookware", "Prep tools", "Small appliances", "Water systems"],
    categoryHints: ["kitchen"],
  },
  {
    id: "fitness",
    name: "Fitness",
    description: "Performance-focused picks for training and recovery goals.",
    href: "/category/fitness",
    eyebrow: "Upcoming",
    featuredBullets: ["Training", "Recovery", "Wearables", "Home gym"],
    categoryHints: ["fitness"],
  },
  {
    id: "travel",
    name: "Travel",
    description: "Curated recommendations for smart travel planning and gear.",
    href: "/category/travel",
    eyebrow: "Upcoming",
    featuredBullets: ["Luggage", "Connectivity", "Safety", "Adapters"],
    categoryHints: ["travel"],
  },
  {
    id: "finance",
    name: "Finance",
    description: "Decision support for cards, savings, and financial tools.",
    href: "/category/finance",
    eyebrow: "Upcoming",
    featuredBullets: ["Cards", "Savings", "Budgeting", "Investing"],
    categoryHints: ["finance"],
  },
  {
    id: "insurance",
    name: "Insurance",
    description: "Policy comparison guidance focused on clarity and trust.",
    href: "/category/insurance",
    eyebrow: "Upcoming",
    featuredBullets: ["Health", "Life", "Travel", "Vehicle"],
    categoryHints: ["insurance"],
  },
];

export const HOMEPAGE_TRUST_SIGNALS: TrustSignal[] = [
  {
    id: "intent-aware-guidance",
    title: "Intent-Aware Guidance",
    description: "Recommendations adapt to budget, priorities, and real usage instead of generic top-ten lists.",
  },
  {
    id: "clear-comparisons",
    title: "Clear Comparisons",
    description: "Every comparison highlights trade-offs that matter in practice, not just spec tables.",
  },
  {
    id: "editorial-context",
    title: "Editorial Context",
    description: "Guides, product rationale, and plain-language summaries help decisions feel less risky.",
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
    id: "iphone-vs-galaxy",
    title: "iPhone 16 Pro vs Galaxy S25",
    subtitle: "Camera consistency, software lifecycle, and resale value.",
    href: "/compare?first=iphone16pro&second=galaxy-s25",
    accent: "from-blue-600 to-violet-600",
  },
  {
    id: "air-vs-zenbook",
    title: "MacBook Air M4 vs ZenBook 14 OLED",
    subtitle: "Battery longevity, build, and performance for coding workflows.",
    href: "/compare?first=macbook-air-m4&second=asus-zenbook-14-oled",
    accent: "from-indigo-600 to-cyan-600",
  },
  {
    id: "sony-vs-bose",
    title: "WH-1000XM6 vs Bose QC Ultra",
    subtitle: "Noise cancellation depth, comfort, and call quality.",
    href: "/compare?first=sony-wh-1000xm6&second=bose-qc-ultra",
    accent: "from-fuchsia-600 to-rose-600",
  },
];

export const HOMEPAGE_TRENDING_SEARCHES: HomeTrendingSearch[] = [
  {
    label: "Best phone under 30000",
    href: "/search?q=Best%20phone%20under%2030000",
    note: "Budget performance",
  },
  {
    label: "Laptop for coding",
    href: "/search?q=Laptop%20for%20coding",
    note: "Developer workflows",
  },
  {
    label: "Headphones for office",
    href: "/search?q=Headphones%20for%20office",
    note: "Comfort and calls",
  },
  {
    label: "Best web hosting",
    href: "/search?q=Best%20web%20hosting",
    note: "Speed and uptime",
  },
  {
    label: "Camera for travel",
    href: "/search?q=Camera%20for%20travel",
    note: "Weight and image quality",
  },
  {
    label: "TV for living room",
    href: "/search?q=TV%20for%20living%20room",
    note: "Room-size fit",
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
    title: "Explore by Category",
    subtitle: "A clean starting point for products, tools, and services we evaluate with the same decision-first lens.",
  },
  {
    id: "trust-letrusto",
    enabled: true,
    order: 3,
    component: "trustSignals",
    dataSource: "trust.default",
    title: "Why Trust LeTrusto",
    subtitle: "Research, comparisons, and recommendation logic designed to make buying decisions clearer and faster.",
  },
  {
    id: "popular-comparisons",
    enabled: true,
    order: 4,
    component: "comparisons",
    dataSource: "comparisons.popular",
    title: "Trending Comparisons",
    subtitle: "Start with the decisions buyers ask us about most.",
    ctaLabel: "Open compare",
    ctaHref: "/compare",
  },
  {
    id: "latest-guides",
    enabled: true,
    order: 5,
    component: "guides",
    dataSource: "guides.latest",
    title: "Latest Buying Guides",
    subtitle: "Editorial intelligence for evaluating trade-offs before you commit.",
    ctaLabel: "All guides",
    ctaHref: "/guides",
    maxItems: 4,
  },
  {
    id: "featured-brands",
    enabled: true,
    order: 6,
    component: "featuredBrands",
    dataSource: "brands.featured",
    title: "Featured Brands",
    subtitle: "Brands currently appearing across the strongest product sets and comparison journeys.",
  },
  {
    id: "trending-searches",
    enabled: true,
    order: 7,
    component: "trendingSearches",
    dataSource: "searches.trending",
    title: "Popular Searches",
    subtitle: "Jump into the most common starting points buyers use when narrowing their shortlist.",
  },
  {
    id: "newsletter",
    enabled: true,
    order: 8,
    component: "newsletter",
    dataSource: "none",
    title: "Get Launch Notes and Buying Updates",
    subtitle: "Receive occasional product research updates, new guides, and major category launches.",
  },
];
