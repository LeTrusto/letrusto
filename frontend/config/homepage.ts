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

export const HOMEPAGE_CATEGORY_CONFIG: HomepageCategoryConfig[] = [
  {
    id: "apparel",
    name: "Apparel",
    description: "Wearable designs printed fresh on tees, sweatshirts, and more.",
    href: "/shop?category=apparel",
    eyebrow: "Wear it",
    featuredBullets: ["T-shirts", "Sweatshirts", "Everyday layers"],
    categoryHints: ["apparel", "clothing", "shirts"],
  },
  {
    id: "wall-art",
    name: "Wall Art",
    description: "Original prints that give your space a point of view.",
    href: "/shop?category=wall-art",
    eyebrow: "Make space",
    featuredBullets: ["Art prints", "Posters", "Gallery walls"],
    categoryHints: ["wall art", "prints", "posters"],
  },
  {
    id: "accessories",
    name: "Accessories",
    description: "Small daily essentials finished with designs worth carrying.",
    href: "/shop?category=accessories",
    eyebrow: "Carry it",
    featuredBullets: ["Phone cases", "Totes", "Everyday essentials"],
    categoryHints: ["accessories", "phone cases", "bags"],
  },
  {
    id: "home-living",
    name: "Home & Living",
    description: "Useful home pieces made more personal with fresh artwork.",
    href: "/shop?category=home-living",
    eyebrow: "Live with it",
    featuredBullets: ["Mugs", "Cushions", "Home accents"],
    categoryHints: ["home", "mugs", "decor"],
  },
  {
    id: "stationery",
    name: "Stationery",
    description: "Thoughtful paper goods for notes, plans, gifts, and ideas.",
    href: "/shop?category=stationery",
    eyebrow: "Put it down",
    featuredBullets: ["Notebooks", "Cards", "Desk goods"],
    categoryHints: ["stationery", "notebooks", "paper goods"],
  },
];

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
