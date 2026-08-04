export type HomeSectionComponent =
  | "hero"
  | "categoryShowcase"
  | "trustSignals"
  | "comparisons"
  | "comingSoonVertical"
  | "guides"
  | "askAiCta";

export type HomeDataSourceKey =
  | "none"
  | "categories.showcase"
  | "trust.default"
  | "comparisons.popular"
  | "comingSoon.hostingSaas"
  | "comingSoon.beauty"
  | "comingSoon.petCare"
  | "guides.latest";

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
};

export type HomepageCategoryConfig = {
  id: string;
  name: string;
  description: string;
  href: string;
  image: string;
  gradientClass: string;
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

export type HomepageComingSoonItem = {
  id: string;
  title: string;
  categoryHref: string;
  description: string;
  illustration: string;
  expectedItems: string[];
};

export const HOMEPAGE_CATEGORY_CONFIG: HomepageCategoryConfig[] = [
  {
    id: "electronics",
    name: "Electronics",
    description: "Phones, laptops, cameras, gaming, and wearables.",
    href: "/category/electronics",
    image: "/images/products/iphone16pro-1.svg",
    gradientClass: "from-indigo-800/90 via-violet-700/85 to-cyan-600/85",
    categoryHints: ["phone", "laptop", "tablet", "camera", "television", "gaming", "headphones", "smartwatch"],
  },
  {
    id: "hosting",
    name: "Hosting",
    description: "Smart recommendations for sites, startups, and growing teams.",
    href: "/category/hosting",
    image: "/images/products/macbook-air-m4.png",
    gradientClass: "from-cyan-800/90 via-blue-700/80 to-indigo-700/85",
    categoryHints: ["hosting", "web-hosting", "cloud", "server"],
  },
  {
    id: "saas",
    name: "SaaS",
    description: "Business software guidance with AI-first evaluation frameworks.",
    href: "/category/saas",
    image: "/images/products/lenovo-legion-go-1.jpg",
    gradientClass: "from-emerald-800/90 via-teal-700/85 to-cyan-700/80",
    categoryHints: ["saas", "software", "productivity", "automation"],
  },
  {
    id: "beauty",
    name: "Beauty",
    description: "Evidence-led recommendations for skincare and wellness.",
    href: "/category/beauty",
    image: "/images/products/sony-a7-iv-1.jpg",
    gradientClass: "from-rose-800/90 via-pink-700/85 to-fuchsia-700/80",
    categoryHints: ["beauty"],
  },
  {
    id: "pet-care",
    name: "Pet Care",
    description: "Trusted picks for food, health, and everyday pet essentials.",
    href: "/category/pet-care",
    image: "/images/products/sony-wh1000xm6.png",
    gradientClass: "from-amber-800/90 via-orange-700/85 to-rose-700/75",
    categoryHints: ["pet-care"],
  },
  {
    id: "home",
    name: "Home",
    description: "Appliance and lifestyle buying guidance for modern homes.",
    href: "/category/home-kitchen",
    image: "/images/products/ifb-senator-mxn-8012-1.jpg",
    gradientClass: "from-slate-800/90 via-indigo-700/80 to-violet-700/80",
    categoryHints: ["home-kitchen", "refrigerator", "washing-machine", "furniture"],
  },
  {
    id: "kitchen",
    name: "Kitchen",
    description: "Compare cooking and prep tools with practical recommendations.",
    href: "/category/kitchen",
    image: "/images/products/whirlpool-stainwash-pro-9kg-1.jpg",
    gradientClass: "from-sky-800/90 via-cyan-700/80 to-blue-700/85",
    categoryHints: ["kitchen"],
  },
  {
    id: "fitness",
    name: "Fitness",
    description: "Performance-focused picks for training and recovery goals.",
    href: "/category/fitness",
    image: "/images/products/samsung-galaxy-tab-s10-1.png",
    gradientClass: "from-lime-800/90 via-emerald-700/85 to-teal-700/80",
    categoryHints: ["fitness"],
  },
  {
    id: "travel",
    name: "Travel",
    description: "Curated recommendations for smart travel planning and gear.",
    href: "/category/travel",
    image: "/images/products/nintendo-switch-oled-1.png",
    gradientClass: "from-blue-800/90 via-sky-700/80 to-teal-700/80",
    categoryHints: ["travel"],
  },
  {
    id: "finance",
    name: "Finance",
    description: "Decision support for cards, savings, and financial tools.",
    href: "/category/finance",
    image: "/images/products/galaxy-s25-1.png",
    gradientClass: "from-emerald-800/90 via-green-700/80 to-cyan-700/75",
    categoryHints: ["finance"],
  },
  {
    id: "insurance",
    name: "Insurance",
    description: "Policy comparison guidance focused on clarity and trust.",
    href: "/category/insurance",
    image: "/images/products/sony-bravia-7-55-1.jpg",
    gradientClass: "from-indigo-900/90 via-violet-700/80 to-fuchsia-700/75",
    categoryHints: ["insurance"],
  },
];

export const HOMEPAGE_TRUST_SIGNALS: TrustSignal[] = [
  {
    id: "ai-recommendations",
    title: "AI Recommendations",
    description: "Intent-aware suggestions tuned to your budget, priorities, and use case.",
  },
  {
    id: "verified-reviews",
    title: "Verified Reviews",
    description: "Buyer feedback and sentiment signals filtered for reliability and relevance.",
  },
  {
    id: "comparisons",
    title: "Deep Comparisons",
    description: "Side-by-side breakdowns that surface practical differences, not just specs.",
  },
  {
    id: "buying-guides",
    title: "Buying Guides",
    description: "Clear editorial guidance that turns research into confident purchase decisions.",
  },
  {
    id: "best-deals",
    title: "Best Value Signals",
    description: "Transparent value indicators that prioritize long-term quality over hype.",
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

export const HOMEPAGE_COMING_SOON_VERTICALS: Record<
  "hostingSaas" | "beauty" | "petCare",
  HomepageComingSoonItem
> = {
  hostingSaas: {
    id: "hosting-saas",
    title: "Hosting & SaaS",
    categoryHref: "/category/hosting",
    description: "We are carefully curating trusted infrastructure and software recommendations for this category.",
    illustration: "HOST",
    expectedItems: [
      "Hostinger",
      "Cloudways",
      "Namecheap",
      "Google Workspace",
      "Website Builders",
      "AI Tools",
    ],
  },
  beauty: {
    id: "beauty",
    title: "Beauty",
    categoryHref: "/category/beauty",
    description: "We are carefully curating the best products and recommendations for this category.",
    illustration: "BEAUTY",
    expectedItems: ["Skincare", "Hair Care", "Wellness", "Cosmetics"],
  },
  petCare: {
    id: "pet-care",
    title: "Pet Care",
    categoryHref: "/category/pet-care",
    description: "We are carefully curating trusted recommendations for pets and their caregivers.",
    illustration: "PET",
    expectedItems: ["Food", "Health", "Accessories", "Training"],
  },
};

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
    subtitle: "Explore research-first buying journeys across present and upcoming verticals.",
  },
  {
    id: "trust-letrusto",
    enabled: true,
    order: 3,
    component: "trustSignals",
    dataSource: "trust.default",
    title: "Why Trust LeTrusto",
    subtitle: "Designed for buyers who want clarity, confidence, and AI-backed guidance.",
  },
  {
    id: "popular-comparisons",
    enabled: true,
    order: 4,
    component: "comparisons",
    dataSource: "comparisons.popular",
    title: "Popular Comparisons",
    subtitle: "Start with the decisions buyers ask us about most.",
    ctaLabel: "Open Comparison Lab",
    ctaHref: "/compare",
  },
  {
    id: "hosting-saas",
    enabled: true,
    order: 5,
    component: "comingSoonVertical",
    dataSource: "comingSoon.hostingSaas",
    title: "Hosting & SaaS",
  },
  {
    id: "beauty",
    enabled: true,
    order: 6,
    component: "comingSoonVertical",
    dataSource: "comingSoon.beauty",
    title: "Beauty",
  },
  {
    id: "pet-care",
    enabled: true,
    order: 7,
    component: "comingSoonVertical",
    dataSource: "comingSoon.petCare",
    title: "Pet Care",
  },
  {
    id: "latest-guides",
    enabled: true,
    order: 8,
    component: "guides",
    dataSource: "guides.latest",
    title: "Latest Buying Guides",
    subtitle: "Editorial intelligence to help you evaluate before you commit.",
    ctaLabel: "All guides",
    ctaHref: "/guides",
    maxItems: 4,
  },
  {
    id: "ask-ai-cta",
    enabled: true,
    order: 9,
    component: "askAiCta",
    dataSource: "none",
    title: "Ask LeTrusto AI",
    subtitle: "Describe what matters to you and get a personalized shortlist in seconds.",
    ctaLabel: "Ask AI Now",
    ctaHref: "/ai",
  },
];
