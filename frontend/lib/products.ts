import type { Product, ProductAvailability, ProductBuyLink, ProductCategory, ProductPriceHistoryPoint, ProductReview, ProductSpecification } from "@/types/products";
import { productImagesById } from "@/lib/productImageManifest";

type ProductSeed = {
  id: string;
  name: string;
  brand: string;
  category: ProductCategory;
  priceValue: number;
  rating: number;
  aiScore: number;
  availability: ProductAvailability;
  features: string[];
  specs: ProductSpecification[];
  pros: string[];
  cons: string[];
  bestFor: string[];
  notRecommendedFor: string[];
  tags: string[];
};

const PRODUCT_IMAGE_VARIANTS = 4;

const CATEGORY_IMAGE_FALLBACKS: Partial<Record<ProductCategory, string[]>> = {
  phone: [
    "/images/products/iphone16pro-1.svg",
    "/images/products/galaxy-s25-1.png",
    "/images/products/nothing-phone-2a-1.jpg",
    "/images/products/oneplus-nord-4-1.jpg",
  ],
  laptop: [
    "/images/products/macbook-air-m4.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/MacBook_Air_M2.png/1280px-MacBook_Air_M2.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/ThinkPad_X1_Carbon_Gen_6.jpg/1280px-ThinkPad_X1_Carbon_Gen_6.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Dell_XPS_13_7390_2-in-1.jpg/1280px-Dell_XPS_13_7390_2-in-1.jpg",
  ],
  headphones: [
    "/images/products/bose-qc-ultra-1.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Sony_WH-1000XM4.jpg/1280px-Sony_WH-1000XM4.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/AirPods_Max.png/1280px-AirPods_Max.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Headphones_1.jpg/1280px-Headphones_1.jpg",
  ],
  smartwatch: [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Samsung_Galaxy_Watch.jpg/1280px-Samsung_Galaxy_Watch.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Apple_Watch.jpg/1280px-Apple_Watch.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Garmin_watch.jpg/1280px-Garmin_watch.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Smart_watch.jpg/1280px-Smart_watch.jpg",
  ],
  television: [
    "/images/products/sony-bravia-7-55-1.jpg",
    "/images/products/tcl-c755-55-1.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Samsung_LED_TV.jpg/1280px-Samsung_LED_TV.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Flat_screen_TV.jpg/1280px-Flat_screen_TV.jpg",
  ],
  refrigerator: [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Open_refrigerator_with_food_at_night.jpg/1280px-Open_refrigerator_with_food_at_night.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Refrigerator.jpg/1280px-Refrigerator.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Fridge_open.jpg/1280px-Fridge_open.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Frigorifero_Double_Door.jpg/1280px-Frigorifero_Double_Door.jpg",
  ],
  "washing-machine": [
    "/images/products/ifb-senator-mxn-8012-1.jpg",
    "/images/products/whirlpool-stainwash-pro-9kg-1.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/e/ec/LG_%EB%93%9C%EB%9F%BC%EC%84%B8%ED%83%81%EA%B8%B0%EC%99%80_%EC%8B%9D%EA%B8%B0%EC%84%B8%EC%B2%99%EA%B8%B0%2C_%EC%98%81%EA%B5%AD%EC%84%9C_%EB%AC%BC%EC%82%AC%EC%9A%A9_%ED%9A%A8%EC%9C%A8_%EC%B5%9C%EC%9A%B0%EC%88%98_%EC%A0%9C%ED%92%88_%EC%88%98%EC%83%81.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Washing_machine.jpg/1280px-Washing_machine.jpg",
  ],
  gaming: [
    "/images/products/nintendo-switch-oled-1.png",
    "/images/products/lenovo-legion-go-1.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Black_and_white_Playstation_5_base_edition_with_controller.png/1280px-Black_and_white_Playstation_5_base_edition_with_controller.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Xbox_series_X_and_series_S_with_controller.jpg/1280px-Xbox_series_X_and_series_S_with_controller.jpg",
  ],
  tablet: [
    "/images/products/ipad-air-m2-1.jpg",
    "/images/products/samsung-galaxy-tab-s10-1.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/IPad_Mini_6_-_1.jpg/1280px-IPad_Mini_6_-_1.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Tablet_computer.jpg/1280px-Tablet_computer.jpg",
  ],
  camera: [
    "/images/products/sony-a7-iv-1.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Canon_EOS_R6.jpg/1280px-Canon_EOS_R6.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Nikon_Z6_camera.jpg/1280px-Nikon_Z6_camera.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Mirrorless_camera.jpg/1280px-Mirrorless_camera.jpg",
  ],
};

export const categoryLabels: Partial<Record<ProductCategory, string>> = {
  phone: "Phone",
  laptop: "Laptop",
  headphones: "Headphones",
  smartwatch: "Smart Watch",
  television: "Television",
  refrigerator: "Refrigerator",
  "washing-machine": "Washing Machine",
  gaming: "Gaming",
  tablet: "Tablet",
  camera: "Camera",
};

export const categoryPluralLabels: Partial<Record<ProductCategory, string>> = {
  phone: "Phones",
  laptop: "Laptops",
  headphones: "Headphones",
  smartwatch: "Smart Watches",
  television: "Televisions",
  refrigerator: "Refrigerators",
  "washing-machine": "Washing Machines",
  gaming: "Gaming",
  tablet: "Tablets",
  camera: "Cameras",
};

export const productSpotlightBadges: Record<string, string> = {
  iphone16pro: "Flagship Pick",
  "galaxy-s25": "Best Seller",
  "nothing-phone-2a": "Budget Favorite",
  "macbook-air-m4": "AI Pick",
  "asus-zenbook-14-oled": "Creator Choice",
  "sony-wh-1000xm6": "Top Rated",
  "bose-qc-ultra": "Travel Favorite",
  "ps5-slim": "Gaming Hit",
  "ipad-air-m2": "Student Pick",
  "sony-a7-iv": "Pro Camera",
};

const priceFormatter = new Intl.NumberFormat("en-IN", {
  maximumFractionDigits: 0,
});

function formatPrice(priceValue: number) {
  return `₹${priceFormatter.format(priceValue)}`;
}

function buildMarketplaceSearchUrl(marketplace: ProductBuyLink["label"], seed: ProductSeed) {
  const query = encodeURIComponent(`${seed.brand} ${seed.name}`);

  switch (marketplace) {
    case "Amazon":
      return `https://www.amazon.in/s?k=${query}`;
    case "Flipkart":
      return `https://www.flipkart.com/search?q=${query}`;
    case "Croma":
      return `https://www.croma.com/searchB?q=${query}%3Arelevance`;
    case "Reliance Digital":
      return `https://www.reliancedigital.in/search?q=${query}`;
    default:
      return `https://www.google.com/search?q=${query}`;
  }
}

function buildBuyLinks(seed: ProductSeed): ProductBuyLink[] {
  return [
    { label: "Amazon", href: buildMarketplaceSearchUrl("Amazon", seed) },
    { label: "Flipkart", href: buildMarketplaceSearchUrl("Flipkart", seed) },
    { label: "Croma", href: buildMarketplaceSearchUrl("Croma", seed) },
    { label: "Reliance Digital", href: buildMarketplaceSearchUrl("Reliance Digital", seed) },
  ];
}

function buildPriceHistory(priceValue: number): ProductPriceHistoryPoint[] {
  const labels = ["Jan", "Feb", "Mar", "Apr", "May", "Now"];
  const multipliers = [1.08, 1.05, 1.03, 1.02, 0.99, 1];

  return labels.map((label, index) => ({
    label,
    price: Math.round((priceValue * multipliers[index]) / 100) * 100,
  }));
}

function buildReviews(name: string, bestFor: string[], pros: string[]): ProductReview[] {
  const firstBenefit = pros[0]?.toLowerCase() ?? "balanced performance";
  const secondBenefit = pros[1]?.toLowerCase() ?? "good everyday usability";
  const primaryUseCase = bestFor[0]?.toLowerCase() ?? "daily use";
  const secondaryUseCase = bestFor[1]?.toLowerCase() ?? "long-term ownership";

  return [
    {
      author: "Aarav S.",
      title: "Worth the shortlist",
      rating: 5,
      comment: `${name} feels polished in daily use and stands out for ${firstBenefit}.`,
      date: "2026-06-03",
    },
    {
      author: "Maya R.",
      title: "Great balance of value and performance",
      rating: 4,
      comment: `I picked it mainly for ${primaryUseCase} and it has delivered consistently so far.`,
      date: "2026-06-19",
    },
    {
      author: "Karthik P.",
      title: "Strong everyday experience",
      rating: 5,
      comment: `Performance is stable, setup is easy, and ${secondBenefit} is noticeable in day-to-day use.`,
      date: "2026-07-02",
    },
    {
      author: "Neha T.",
      title: "Good with a few tradeoffs",
      rating: 4,
      comment: `The strengths are clear, but buyers should still weigh the compromises against ${secondaryUseCase}.`,
      date: "2026-07-11",
    },
    {
      author: "Rahul D.",
      title: "Would recommend",
      rating: 5,
      comment: `For anyone prioritizing ${secondaryUseCase}, this is easy to recommend.`,
      date: "2026-07-22",
    },
  ];
}

function buildDescription(seed: ProductSeed) {
  return `${seed.brand} ${seed.name} is a ${(categoryLabels[seed.category] ?? seed.category).toLowerCase()} built for ${seed.bestFor[0].toLowerCase()}, with ${seed.features[0].toLowerCase()} and ${seed.features[1].toLowerCase()} leading the experience.`;
}

function buildAiSummary(seed: ProductSeed) {
  const topSpecs = seed.specs.slice(0, 2).map((spec) => `${spec.label}: ${spec.value}`).join("; ");
  const priceBand = seed.priceValue >= 100000 ? "premium" : seed.priceValue >= 50000 ? "upper-mid" : "value";

  return `${seed.name} is rated ${seed.aiScore}/100 in our ${priceBand} segment scoring. It stands out for ${seed.features[0].toLowerCase()} and ${seed.features[1].toLowerCase()}, while spec highlights include ${topSpecs}. Recommended for ${seed.bestFor[0].toLowerCase()} and ${seed.bestFor[1].toLowerCase()}.`;
}

function buildReviewSummary(seed: ProductSeed) {
  return `Buyer sentiment is mostly positive, with repeat praise for ${seed.pros[0].toLowerCase()} and ${seed.pros[1].toLowerCase()}. The most common caution is ${seed.cons[0].toLowerCase()}, especially among users with ${seed.notRecommendedFor[0].toLowerCase()}.`;
}

function buildFallbackImage(seed: ProductSeed) {
  return (CATEGORY_IMAGE_FALLBACKS[seed.category] ?? CATEGORY_IMAGE_FALLBACKS["phone"] ?? [])[0] ?? "";
}

function buildProductGallery(seed: ProductSeed) {
  const directImages = productImagesById[seed.id] ?? [];
  const categoryImages = CATEGORY_IMAGE_FALLBACKS[seed.category] ?? [];

  const deduped = [...directImages, ...categoryImages].filter((image, index, list) => {
    return Boolean(image) && list.indexOf(image) === index;
  });

  if (deduped.length >= PRODUCT_IMAGE_VARIANTS) {
    return deduped.slice(0, PRODUCT_IMAGE_VARIANTS);
  }

  if (deduped.length === 0) {
    return [buildFallbackImage(seed)];
  }

  const filled = [...deduped];
  while (filled.length < PRODUCT_IMAGE_VARIANTS) {
    filled.push(deduped[filled.length % deduped.length]);
  }

  return filled.slice(0, PRODUCT_IMAGE_VARIANTS);
}

function createProduct(seed: ProductSeed): Product {
  const images = buildProductGallery(seed);
  const fallbackImage = images[0] ?? buildFallbackImage(seed);

  return {
    ...seed,
    price: formatPrice(seed.priceValue),
    image: images[0],
    images,
    fallbackImage,
    description: buildDescription(seed),
    aiSummary: buildAiSummary(seed),
    priceHistory: buildPriceHistory(seed.priceValue),
    reviews: buildReviews(seed.name, seed.bestFor, seed.pros),
    reviewSummary: buildReviewSummary(seed),
    buyLinks: buildBuyLinks(seed),
    similarProductIds: [],
  };
}

const productSeeds: ProductSeed[] = [
  {
    id: "iphone16pro",
    name: "iPhone 16 Pro",
    brand: "Apple",
    category: "phone",
    priceValue: 119900,
    rating: 4.8,
    aiScore: 95,
    availability: "In Stock",
    features: ["Excellent Camera", "A18 Pro performance", "Titanium design", "Long software support"],
    specs: [
      { label: "Display", value: "6.3-inch Super Retina XDR" },
      { label: "Chip", value: "Apple A18 Pro" },
      { label: "Storage", value: "256GB" },
      { label: "Battery", value: "Up to 27 hours video" },
      { label: "Camera", value: "48MP Pro camera system" },
    ],
    pros: ["Excellent low-light camera performance", "Premium compact build", "Strong software longevity"],
    cons: ["High price for mainstream buyers", "Closed ecosystem for Android users"],
    bestFor: ["mobile photography", "long-term flagship buyers"],
    notRecommendedFor: ["strict budget shopping", "users who prefer Android customization"],
    tags: ["iphone", "apple", "ios", "flagship", "camera", "phone"],
  },
  {
    id: "galaxy-s25",
    name: "Galaxy S25",
    brand: "Samsung",
    category: "phone",
    priceValue: 84999,
    rating: 4.7,
    aiScore: 92,
    availability: "In Stock",
    features: ["Bright AMOLED display", "Flagship Android performance", "Reliable battery life", "Versatile camera setup"],
    specs: [
      { label: "Display", value: "6.2-inch Dynamic AMOLED" },
      { label: "Chip", value: "Snapdragon Elite" },
      { label: "Storage", value: "256GB" },
      { label: "Battery", value: "4,700mAh" },
      { label: "Camera", value: "50MP AI camera system" },
    ],
    pros: ["Balanced flagship value", "Excellent display quality", "Strong battery life"],
    cons: ["Camera can be inconsistent in motion", "UI may feel busy to some users"],
    bestFor: ["Android flagship buyers", "everyday photography"],
    notRecommendedFor: ["minimal software preferences", "compact-phone enthusiasts"],
    tags: ["samsung", "android", "mobile", "camera", "display", "phone"],
  },
  {
    id: "nothing-phone-2a",
    name: "Nothing Phone 2a",
    brand: "Nothing",
    category: "phone",
    priceValue: 27999,
    rating: 4.5,
    aiScore: 90,
    availability: "In Stock",
    features: ["Clean Android experience", "Distinctive design", "Strong battery efficiency", "Balanced cameras"],
    specs: [
      { label: "Display", value: "6.7-inch AMOLED 120Hz" },
      { label: "Chip", value: "Dimensity 7200 Pro" },
      { label: "Storage", value: "256GB" },
      { label: "Battery", value: "5,000mAh" },
      { label: "Camera", value: "50MP dual camera" },
    ],
    pros: ["Great value under 30000", "Clean software without bloat", "Unique design language"],
    cons: ["Performance is not flagship-level", "Low-light camera remains average"],
    bestFor: ["budget phone buyers", "clean Android fans"],
    notRecommendedFor: ["heavy mobile gaming", "telephoto camera needs"],
    tags: ["nothing", "budget", "under 30000", "android", "phone", "mobile"],
  },
  {
    id: "oneplus-nord-4",
    name: "OnePlus Nord 4",
    brand: "OnePlus",
    category: "phone",
    priceValue: 28999,
    rating: 4.5,
    aiScore: 91,
    availability: "In Stock",
    features: ["Fast charging", "Smooth OxygenOS", "Strong everyday speed", "Solid AMOLED panel"],
    specs: [
      { label: "Display", value: "6.74-inch AMOLED 120Hz" },
      { label: "Chip", value: "Snapdragon 7+ Gen 3" },
      { label: "Storage", value: "256GB" },
      { label: "Battery", value: "5,500mAh" },
      { label: "Charging", value: "100W SUPERVOOC" },
    ],
    pros: ["Fast charging is genuinely useful", "Fluid software experience", "Strong value at its price"],
    cons: ["Camera tuning is only decent", "No standout zoom option"],
    bestFor: ["buyers wanting speed on a budget", "students and office users"],
    notRecommendedFor: ["camera-first shoppers", "premium flagship seekers"],
    tags: ["oneplus", "nord", "budget", "phone", "android", "under 30000"],
  },
  {
    id: "motorola-edge-50-pro",
    name: "Motorola Edge 50 Pro",
    brand: "Motorola",
    category: "phone",
    priceValue: 27999,
    rating: 4.4,
    aiScore: 89,
    availability: "Limited Stock",
    features: ["Curved pOLED display", "Fast wireless charging", "Near-stock Android", "Lightweight build"],
    specs: [
      { label: "Display", value: "6.7-inch pOLED 144Hz" },
      { label: "Chip", value: "Snapdragon 7 Gen 3" },
      { label: "Storage", value: "256GB" },
      { label: "Battery", value: "4,500mAh" },
      { label: "Charging", value: "125W wired / 50W wireless" },
    ],
    pros: ["Premium feel under 30000", "Clean software experience", "Fast charging versatility"],
    cons: ["Battery endurance is only average", "Curved display is subjective"],
    bestFor: ["design-conscious buyers", "fast charging priorities"],
    notRecommendedFor: ["flat-display purists", "power users wanting bigger battery"],
    tags: ["motorola", "edge", "under 30000", "phone", "android", "budget"],
  },
  {
    id: "macbook-air-m4",
    name: "MacBook Air M4",
    brand: "Apple",
    category: "laptop",
    priceValue: 99900,
    rating: 4.9,
    aiScore: 97,
    availability: "In Stock",
    features: ["Outstanding battery life", "Strong coding performance", "Silent fanless design", "Premium portability"],
    specs: [
      { label: "Display", value: "13.6-inch Liquid Retina" },
      { label: "Chip", value: "Apple M4" },
      { label: "Memory", value: "16GB unified memory" },
      { label: "Storage", value: "512GB SSD" },
      { label: "Battery", value: "Up to 18 hours" },
    ],
    pros: ["Excellent performance-per-watt", "Very portable chassis", "Battery lasts all day"],
    cons: ["Limited ports", "macOS is not ideal for every workflow"],
    bestFor: ["coding and office work", "students wanting portability"],
    notRecommendedFor: ["users needing many ports", "Windows-only enterprise workflows"],
    tags: ["macbook", "apple", "laptop", "coding", "developer", "office"],
  },
  {
    id: "asus-zenbook-14-oled",
    name: "Zenbook 14 OLED",
    brand: "ASUS",
    category: "laptop",
    priceValue: 89990,
    rating: 4.7,
    aiScore: 93,
    availability: "In Stock",
    features: ["OLED display", "Slim metal build", "Strong multitasking", "Good port selection"],
    specs: [
      { label: "Display", value: "14-inch 3K OLED" },
      { label: "Chip", value: "Intel Core Ultra 7" },
      { label: "Memory", value: "16GB LPDDR5X" },
      { label: "Storage", value: "1TB SSD" },
      { label: "Battery", value: "75Wh" },
    ],
    pros: ["Gorgeous OLED panel", "Lightweight for travel", "Useful mix of ports"],
    cons: ["Battery life trails MacBook", "Fan noise appears under load"],
    bestFor: ["Windows productivity", "content consumption and work"],
    notRecommendedFor: ["silent-workflow expectations", "heavy 3D rendering"],
    tags: ["asus", "zenbook", "laptop", "office", "oled", "windows"],
  },
  {
    id: "lenovo-thinkpad-x1-carbon",
    name: "ThinkPad X1 Carbon Gen 12",
    brand: "Lenovo",
    category: "laptop",
    priceValue: 149990,
    rating: 4.8,
    aiScore: 94,
    availability: "Limited Stock",
    features: ["Legendary keyboard", "Enterprise security", "Light carbon chassis", "Reliable Linux compatibility"],
    specs: [
      { label: "Display", value: "14-inch 2.8K OLED" },
      { label: "Chip", value: "Intel Core Ultra 7" },
      { label: "Memory", value: "32GB LPDDR5X" },
      { label: "Storage", value: "1TB SSD" },
      { label: "Weight", value: "1.09kg" },
    ],
    pros: ["Excellent keyboard for long typing", "Strong enterprise fit", "Very portable premium build"],
    cons: ["Expensive for most buyers", "Speakers are only average"],
    bestFor: ["business travel", "developers who type all day"],
    notRecommendedFor: ["tight budgets", "buyers focused on media speakers"],
    tags: ["lenovo", "thinkpad", "laptop", "developer", "business", "office"],
  },
  {
    id: "dell-xps-13",
    name: "XPS 13",
    brand: "Dell",
    category: "laptop",
    priceValue: 139990,
    rating: 4.6,
    aiScore: 91,
    availability: "Pre-order",
    features: ["Compact premium design", "High-resolution display", "Fast SSD storage", "Polished trackpad"],
    specs: [
      { label: "Display", value: "13.4-inch 3K OLED" },
      { label: "Chip", value: "Intel Core Ultra 7" },
      { label: "Memory", value: "16GB LPDDR5X" },
      { label: "Storage", value: "1TB SSD" },
      { label: "Battery", value: "55Wh" },
    ],
    pros: ["Premium industrial design", "Sharp display quality", "Great portability"],
    cons: ["Limited connectivity", "Thermals can rise under sustained load"],
    bestFor: ["premium Windows portability", "executive travel"],
    notRecommendedFor: ["heavy sustained workloads", "users needing many native ports"],
    tags: ["dell", "xps", "laptop", "premium", "windows", "office"],
  },
  {
    id: "hp-spectre-x360-14",
    name: "Spectre x360 14",
    brand: "HP",
    category: "laptop",
    priceValue: 129990,
    rating: 4.6,
    aiScore: 90,
    availability: "In Stock",
    features: ["Convertible design", "OLED touchscreen", "Stylus support", "Premium finish"],
    specs: [
      { label: "Display", value: "14-inch 2.8K OLED Touch" },
      { label: "Chip", value: "Intel Core Ultra 7" },
      { label: "Memory", value: "16GB LPDDR5X" },
      { label: "Storage", value: "1TB SSD" },
      { label: "Battery", value: "68Wh" },
    ],
    pros: ["Versatile 2-in-1 design", "Good pen support", "Premium display and build"],
    cons: ["Heavier than a traditional ultrabook", "Can get warm in tablet mode"],
    bestFor: ["creative note-taking", "flexible work and entertainment"],
    notRecommendedFor: ["users who never use tablet mode", "buyers chasing lowest weight"],
    tags: ["hp", "spectre", "laptop", "touchscreen", "office", "creator"],
  },
  {
    id: "sony-wh-1000xm6",
    name: "WH-1000XM6",
    brand: "Sony",
    category: "headphones",
    priceValue: 29990,
    rating: 4.8,
    aiScore: 94,
    availability: "In Stock",
    features: ["Class-leading noise cancellation", "Rich audio tuning", "Long battery life", "Excellent travel comfort"],
    specs: [
      { label: "Driver", value: "30mm dynamic" },
      { label: "Battery", value: "30 hours" },
      { label: "Connectivity", value: "Bluetooth 5.4 multipoint" },
      { label: "Charging", value: "USB-C fast charge" },
      { label: "Weight", value: "Approx. 250g" },
    ],
    pros: ["Best-in-class ANC", "Comfortable for long sessions", "Balanced sound quality"],
    cons: ["Premium price", "Touch controls need familiarization"],
    bestFor: ["office focus and travel", "daily music listening"],
    notRecommendedFor: ["budget audio shopping", "users preferring physical controls"],
    tags: ["sony", "headphones", "music", "noise cancellation", "office", "travel"],
  },
  {
    id: "bose-qc-ultra",
    name: "QuietComfort Ultra",
    brand: "Bose",
    category: "headphones",
    priceValue: 34990,
    rating: 4.7,
    aiScore: 93,
    availability: "In Stock",
    features: ["Top-tier comfort", "Immersive spatial audio", "Strong ANC", "Reliable call quality"],
    specs: [
      { label: "Driver", value: "Custom dynamic drivers" },
      { label: "Battery", value: "24 hours" },
      { label: "Connectivity", value: "Bluetooth 5.3" },
      { label: "Charging", value: "USB-C" },
      { label: "Weight", value: "Approx. 254g" },
    ],
    pros: ["Superb wearing comfort", "Excellent ANC for flights", "Very clean voice pickup"],
    cons: ["Battery trails Sony", "Spatial audio is not for everyone"],
    bestFor: ["frequent travelers", "office calls and commuting"],
    notRecommendedFor: ["buyers prioritizing battery life", "tight mid-range budgets"],
    tags: ["bose", "headphones", "travel", "office", "noise cancellation", "music"],
  },
  {
    id: "airpods-max",
    name: "AirPods Max",
    brand: "Apple",
    category: "headphones",
    priceValue: 59900,
    rating: 4.6,
    aiScore: 90,
    availability: "In Stock",
    features: ["Seamless Apple integration", "Premium build", "Spatial audio", "Strong ANC"],
    specs: [
      { label: "Chip", value: "Apple H1 dual-chip" },
      { label: "Battery", value: "20 hours" },
      { label: "Connectivity", value: "Bluetooth 5.0" },
      { label: "Charging", value: "USB-C" },
      { label: "Weight", value: "Approx. 384g" },
    ],
    pros: ["Excellent Apple ecosystem fit", "Premium materials", "Great transparency mode"],
    cons: ["Very expensive", "Heavy for long listening sessions"],
    bestFor: ["Apple ecosystem buyers", "premium home and office listening"],
    notRecommendedFor: ["lightweight comfort priorities", "value-focused shoppers"],
    tags: ["apple", "airpods", "headphones", "music", "office", "premium"],
  },
  {
    id: "sennheiser-momentum-4",
    name: "Momentum 4",
    brand: "Sennheiser",
    category: "headphones",
    priceValue: 27990,
    rating: 4.6,
    aiScore: 91,
    availability: "Limited Stock",
    features: ["Audiophile-friendly tuning", "Long battery life", "Good comfort", "Effective ANC"],
    specs: [
      { label: "Driver", value: "42mm transducer system" },
      { label: "Battery", value: "60 hours" },
      { label: "Connectivity", value: "Bluetooth 5.2" },
      { label: "Charging", value: "USB-C" },
      { label: "Weight", value: "Approx. 293g" },
    ],
    pros: ["Excellent sound quality", "Huge battery life", "Good value against premium rivals"],
    cons: ["App experience is only okay", "ANC is a step behind the very best"],
    bestFor: ["music-first buyers", "long battery needs"],
    notRecommendedFor: ["buyers wanting best ANC only", "users who dislike bulkier cups"],
    tags: ["sennheiser", "headphones", "music", "battery", "office", "travel"],
  },
  {
    id: "jbl-tour-one-m2",
    name: "Tour One M2",
    brand: "JBL",
    category: "headphones",
    priceValue: 24999,
    rating: 4.4,
    aiScore: 87,
    availability: "In Stock",
    features: ["Punchy sound", "Adaptive ANC", "Long battery", "Useful companion app"],
    specs: [
      { label: "Driver", value: "40mm dynamic" },
      { label: "Battery", value: "50 hours" },
      { label: "Connectivity", value: "Bluetooth 5.3" },
      { label: "Charging", value: "USB-C" },
      { label: "Weight", value: "Approx. 278g" },
    ],
    pros: ["Competitive price", "Battery life is strong", "Fun mainstream sound"],
    cons: ["Build does not feel as premium", "Tuning may be bass-heavy for some"],
    bestFor: ["value-conscious headphone buyers", "casual commuting and office use"],
    notRecommendedFor: ["neutral-sound purists", "luxury build expectations"],
    tags: ["jbl", "headphones", "budget", "music", "office", "travel"],
  },
  {
    id: "apple-watch-series-10",
    name: "Watch Series 10",
    brand: "Apple",
    category: "smartwatch",
    priceValue: 49900,
    rating: 4.8,
    aiScore: 94,
    availability: "In Stock",
    features: ["Best iPhone integration", "Strong health tracking", "Bright display", "Smooth watchOS apps"],
    specs: [
      { label: "Display", value: "Always-on OLED" },
      { label: "Chip", value: "Apple S10" },
      { label: "Battery", value: "Up to 18 hours" },
      { label: "Sensors", value: "ECG, SpO2, temperature" },
      { label: "Connectivity", value: "GPS + optional Cellular" },
    ],
    pros: ["Best smartwatch app ecosystem", "Excellent fitness and health tracking", "Responsive performance"],
    cons: ["Works best only with iPhone", "Battery still needs daily charging"],
    bestFor: ["iPhone users", "health and fitness tracking"],
    notRecommendedFor: ["Android phone owners", "multi-day battery expectations"],
    tags: ["apple", "watch", "smartwatch", "fitness", "wearable", "health"],
  },
  {
    id: "samsung-galaxy-watch-7",
    name: "Galaxy Watch 7",
    brand: "Samsung",
    category: "smartwatch",
    priceValue: 32999,
    rating: 4.6,
    aiScore: 90,
    availability: "In Stock",
    features: ["Great Android integration", "Useful health features", "Bright AMOLED screen", "Compact design"],
    specs: [
      { label: "Display", value: "Super AMOLED" },
      { label: "Chip", value: "Exynos W1000" },
      { label: "Battery", value: "Up to 40 hours" },
      { label: "Sensors", value: "BioActive sensor" },
      { label: "Connectivity", value: "Bluetooth / LTE variants" },
    ],
    pros: ["Strong Android smartwatch choice", "Bright responsive display", "Good health tracking"],
    cons: ["Best features need Samsung phone", "Battery is still not class-leading"],
    bestFor: ["Android and Samsung users", "fitness and notifications"],
    notRecommendedFor: ["iPhone owners", "users wanting week-long battery"],
    tags: ["samsung", "watch", "smartwatch", "android", "fitness", "wearable"],
  },
  {
    id: "garmin-venu-3",
    name: "Venu 3",
    brand: "Garmin",
    category: "smartwatch",
    priceValue: 42990,
    rating: 4.7,
    aiScore: 91,
    availability: "Limited Stock",
    features: ["Excellent battery life", "Advanced recovery metrics", "Great workout tracking", "Bright AMOLED"],
    specs: [
      { label: "Display", value: "1.4-inch AMOLED" },
      { label: "Battery", value: "Up to 14 days" },
      { label: "GPS", value: "Multi-band GPS" },
      { label: "Sensors", value: "Heart rate, Body Battery, Sleep Coach" },
      { label: "Water Resistance", value: "5 ATM" },
    ],
    pros: ["Battery lasts much longer", "Excellent fitness insights", "Works well across platforms"],
    cons: ["Smart app ecosystem is limited", "Price is high for casual users"],
    bestFor: ["fitness-first buyers", "multi-day battery needs"],
    notRecommendedFor: ["app-heavy smartwatch expectations", "budget shoppers"],
    tags: ["garmin", "venu", "smartwatch", "fitness", "health", "battery"],
  },
  {
    id: "oneplus-watch-2",
    name: "Watch 2",
    brand: "OnePlus",
    category: "smartwatch",
    priceValue: 24999,
    rating: 4.4,
    aiScore: 86,
    availability: "In Stock",
    features: ["Strong battery life", "Wear OS support", "Premium stainless steel look", "Snappy performance"],
    specs: [
      { label: "Display", value: "1.43-inch AMOLED" },
      { label: "Chip", value: "Snapdragon W5 + BES2700" },
      { label: "Battery", value: "Up to 100 hours" },
      { label: "GPS", value: "Dual-frequency GPS" },
      { label: "Water Resistance", value: "5 ATM + IP68" },
    ],
    pros: ["Excellent battery for Wear OS", "Premium build at the price", "Good notification handling"],
    cons: ["Health metrics lag leaders", "Bulky for small wrists"],
    bestFor: ["Android users wanting long battery", "notification-heavy daily use"],
    notRecommendedFor: ["small wrist comfort", "serious athlete metrics"],
    tags: ["oneplus", "watch", "smartwatch", "android", "battery", "wearable"],
  },
  {
    id: "amazfit-balance",
    name: "Balance",
    brand: "Amazfit",
    category: "smartwatch",
    priceValue: 19999,
    rating: 4.3,
    aiScore: 84,
    availability: "In Stock",
    features: ["Long battery life", "Lightweight design", "Strong wellness metrics", "Affordable price"],
    specs: [
      { label: "Display", value: "1.5-inch AMOLED" },
      { label: "Battery", value: "Up to 14 days" },
      { label: "GPS", value: "Dual-band GPS" },
      { label: "Sensors", value: "Heart rate, stress, sleep" },
      { label: "Weight", value: "Approx. 35g" },
    ],
    pros: ["Great value for wellness tracking", "Very good battery life", "Comfortable for all-day wear"],
    cons: ["App store is limited", "Notifications feel basic"],
    bestFor: ["budget wearable shoppers", "wellness and sleep tracking"],
    notRecommendedFor: ["rich app ecosystem needs", "advanced smartwatch apps"],
    tags: ["amazfit", "watch", "smartwatch", "budget", "fitness", "health"],
  },
  {
    id: "lg-oled-evo-c4-55",
    name: "OLED evo C4 55",
    brand: "LG",
    category: "television",
    priceValue: 149990,
    rating: 4.8,
    aiScore: 95,
    availability: "In Stock",
    features: ["OLED contrast", "Excellent gaming features", "Strong upscaling", "Premium design"],
    specs: [
      { label: "Screen Size", value: "55-inch" },
      { label: "Panel", value: "OLED evo 4K" },
      { label: "Refresh Rate", value: "120Hz" },
      { label: "HDMI", value: "4 x HDMI 2.1" },
      { label: "OS", value: "webOS" },
    ],
    pros: ["Outstanding contrast and blacks", "Excellent for PS5 and Xbox", "Great movie experience"],
    cons: ["Premium price", "Brightness trails best mini-LED sets in sunny rooms"],
    bestFor: ["cinematic home viewing", "console gaming"],
    notRecommendedFor: ["very bright living rooms", "entry-level budgets"],
    tags: ["lg", "tv", "television", "oled", "gaming", "movies"],
  },
  {
    id: "samsung-qn90d-55",
    name: "QN90D Neo QLED 55",
    brand: "Samsung",
    category: "television",
    priceValue: 159990,
    rating: 4.7,
    aiScore: 93,
    availability: "In Stock",
    features: ["Very high brightness", "Excellent anti-reflection", "Strong gaming mode", "Vivid QLED colors"],
    specs: [
      { label: "Screen Size", value: "55-inch" },
      { label: "Panel", value: "Neo QLED 4K" },
      { label: "Refresh Rate", value: "144Hz" },
      { label: "HDMI", value: "4 x HDMI 2.1" },
      { label: "OS", value: "Tizen" },
    ],
    pros: ["Excellent brightness for bright rooms", "Great gaming features", "Very good color punch"],
    cons: ["Black levels are not OLED-grade", "Price is still premium"],
    bestFor: ["bright living rooms", "sports and gaming"],
    notRecommendedFor: ["OLED black-level purists", "budget-conscious buyers"],
    tags: ["samsung", "tv", "television", "qled", "gaming", "sports"],
  },
  {
    id: "sony-bravia-7-55",
    name: "Bravia 7 55",
    brand: "Sony",
    category: "television",
    priceValue: 169990,
    rating: 4.7,
    aiScore: 94,
    availability: "Limited Stock",
    features: ["Excellent motion handling", "Strong cinematic processing", "Balanced mini-LED picture", "Google TV"],
    specs: [
      { label: "Screen Size", value: "55-inch" },
      { label: "Panel", value: "Mini LED 4K" },
      { label: "Refresh Rate", value: "120Hz" },
      { label: "HDMI", value: "4 ports, 2 x HDMI 2.1" },
      { label: "OS", value: "Google TV" },
    ],
    pros: ["Excellent motion and upscaling", "Strong movie performance", "Good Google TV ecosystem"],
    cons: ["Two HDMI 2.1 ports only", "Expensive versus TCL alternatives"],
    bestFor: ["film enthusiasts", "balanced movie and gaming use"],
    notRecommendedFor: ["buyers needing four HDMI 2.1 ports", "value-first shoppers"],
    tags: ["sony", "tv", "television", "movies", "google tv", "gaming"],
  },
  {
    id: "tcl-c755-55",
    name: "C755 55",
    brand: "TCL",
    category: "television",
    priceValue: 89990,
    rating: 4.5,
    aiScore: 89,
    availability: "In Stock",
    features: ["Great value mini-LED", "High brightness", "Google TV", "Good gaming features"],
    specs: [
      { label: "Screen Size", value: "55-inch" },
      { label: "Panel", value: "Mini LED 4K" },
      { label: "Refresh Rate", value: "144Hz" },
      { label: "HDMI", value: "4 ports" },
      { label: "OS", value: "Google TV" },
    ],
    pros: ["Strong value for performance", "Bright enough for most rooms", "Useful gaming feature set"],
    cons: ["Build feels less premium", "Picture processing lags Sony and LG"],
    bestFor: ["value-focused TV upgrades", "gaming on a budget"],
    notRecommendedFor: ["premium build expectations", "best-in-class processing needs"],
    tags: ["tcl", "tv", "television", "budget", "gaming", "qled"],
  },
  {
    id: "hisense-u7n-55",
    name: "U7N 55",
    brand: "Hisense",
    category: "television",
    priceValue: 79990,
    rating: 4.4,
    aiScore: 87,
    availability: "In Stock",
    features: ["Competitive brightness", "Good gaming specs", "Strong price-to-performance", "Mini-LED backlight"],
    specs: [
      { label: "Screen Size", value: "55-inch" },
      { label: "Panel", value: "Mini LED 4K" },
      { label: "Refresh Rate", value: "144Hz" },
      { label: "HDMI", value: "4 ports" },
      { label: "OS", value: "VIDAA" },
    ],
    pros: ["Aggressive value", "Solid HDR brightness", "Good choice for casual gaming"],
    cons: ["Software ecosystem is smaller", "Processing is not class-leading"],
    bestFor: ["budget-conscious living rooms", "casual gaming and streaming"],
    notRecommendedFor: ["premium OS expectations", "high-end home theater tuning"],
    tags: ["hisense", "tv", "television", "budget", "gaming", "streaming"],
  },
  {
    id: "samsung-bespoke-415l",
    name: "Bespoke 415L",
    brand: "Samsung",
    category: "refrigerator",
    priceValue: 55990,
    rating: 4.5,
    aiScore: 88,
    availability: "In Stock",
    features: ["Convertible storage modes", "Digital inverter compressor", "Modern finish", "Efficient cooling"],
    specs: [
      { label: "Capacity", value: "415L" },
      { label: "Cooling", value: "Twin Cooling Plus" },
      { label: "Compressor", value: "Digital Inverter" },
      { label: "Design", value: "Frost-free double door" },
      { label: "Energy Rating", value: "3 Star" },
    ],
    pros: ["Flexible storage modes", "Modern kitchen look", "Reliable cooling performance"],
    cons: ["Energy rating is only moderate", "Premium finish raises price"],
    bestFor: ["modern family kitchens", "buyers wanting flexible storage"],
    notRecommendedFor: ["very small kitchens", "strict low-budget replacements"],
    tags: ["samsung", "refrigerator", "fridge", "kitchen", "family", "appliance"],
  },
  {
    id: "lg-instaview-655l",
    name: "Instaview 655L",
    brand: "LG",
    category: "refrigerator",
    priceValue: 119990,
    rating: 4.7,
    aiScore: 92,
    availability: "Limited Stock",
    features: ["Large premium capacity", "Door-in-door access", "Hygiene fresh filtration", "Linear cooling"],
    specs: [
      { label: "Capacity", value: "655L" },
      { label: "Cooling", value: "DoorCooling+" },
      { label: "Compressor", value: "Smart Inverter" },
      { label: "Design", value: "Side-by-side InstaView" },
      { label: "Energy Rating", value: "2 Star" },
    ],
    pros: ["Huge capacity for large families", "Premium convenience features", "Consistent cooling"],
    cons: ["Expensive", "Needs substantial kitchen space"],
    bestFor: ["large households", "premium kitchen upgrades"],
    notRecommendedFor: ["small apartments", "cost-sensitive buyers"],
    tags: ["lg", "refrigerator", "fridge", "premium", "family", "appliance"],
  },
  {
    id: "whirlpool-proton-340l",
    name: "Proton 340L",
    brand: "Whirlpool",
    category: "refrigerator",
    priceValue: 38990,
    rating: 4.4,
    aiScore: 84,
    availability: "In Stock",
    features: ["Convertible freezer", "Good storage layout", "Intellisense inverter", "Value-focused pricing"],
    specs: [
      { label: "Capacity", value: "340L" },
      { label: "Cooling", value: "Frost-free" },
      { label: "Compressor", value: "Intellisense Inverter" },
      { label: "Design", value: "Double door" },
      { label: "Energy Rating", value: "3 Star" },
    ],
    pros: ["Good everyday value", "Flexible freezer section", "Suitable for mid-size families"],
    cons: ["Fit and finish is basic", "No premium freshness features"],
    bestFor: ["mid-size households", "value upgrades from older fridges"],
    notRecommendedFor: ["premium kitchen aesthetics", "very large families"],
    tags: ["whirlpool", "refrigerator", "fridge", "budget", "family", "appliance"],
  },
  {
    id: "haier-bottom-mount-325l",
    name: "Bottom Mount 325L",
    brand: "Haier",
    category: "refrigerator",
    priceValue: 34990,
    rating: 4.3,
    aiScore: 82,
    availability: "In Stock",
    features: ["Bottom freezer design", "Modern layout", "1-hour icing", "Affordable pricing"],
    specs: [
      { label: "Capacity", value: "325L" },
      { label: "Cooling", value: "Frost-free" },
      { label: "Compressor", value: "Inverter" },
      { label: "Design", value: "Bottom mount" },
      { label: "Energy Rating", value: "2 Star" },
    ],
    pros: ["Convenient fridge-on-top layout", "Good value for style", "Compact family fit"],
    cons: ["Energy efficiency is average", "Brand service varies by area"],
    bestFor: ["compact modern kitchens", "style-conscious buyers on a budget"],
    notRecommendedFor: ["buyers prioritizing best service network", "large storage needs"],
    tags: ["haier", "refrigerator", "fridge", "budget", "kitchen", "appliance"],
  },
  {
    id: "godrej-edge-pro-310l",
    name: "Edge Pro 310L",
    brand: "Godrej",
    category: "refrigerator",
    priceValue: 31990,
    rating: 4.2,
    aiScore: 81,
    availability: "In Stock",
    features: ["Nano shield technology", "SpaceMax layout", "Inverter compressor", "Strong value"],
    specs: [
      { label: "Capacity", value: "310L" },
      { label: "Cooling", value: "Frost-free" },
      { label: "Compressor", value: "Advanced Inverter" },
      { label: "Design", value: "Double door" },
      { label: "Energy Rating", value: "3 Star" },
    ],
    pros: ["Affordable entry to frost-free segment", "Useful storage layout", "Good everyday cooling"],
    cons: ["Basic premium feel", "Fewer smart features"],
    bestFor: ["family essentials on a budget", "first appliance upgrades"],
    notRecommendedFor: ["premium kitchen designs", "large households"],
    tags: ["godrej", "refrigerator", "fridge", "budget", "family", "appliance"],
  },
  {
    id: "lg-front-load-9kg",
    name: "Front Load 9kg",
    brand: "LG",
    category: "washing-machine",
    priceValue: 47990,
    rating: 4.6,
    aiScore: 89,
    availability: "In Stock",
    features: ["Steam wash", "AI Direct Drive", "Quiet operation", "Large family capacity"],
    specs: [
      { label: "Type", value: "Front load" },
      { label: "Capacity", value: "9kg" },
      { label: "Motor", value: "Inverter Direct Drive" },
      { label: "Programs", value: "10+ wash programs" },
      { label: "Smart Features", value: "ThinQ connectivity" },
    ],
    pros: ["Excellent wash quality", "Quiet and refined operation", "Good fabric care"],
    cons: ["Costs more than top load models", "Cycle times are longer"],
    bestFor: ["families wanting premium wash care", "noise-sensitive homes"],
    notRecommendedFor: ["very fast daily washes only", "entry-level appliance budgets"],
    tags: ["lg", "washing machine", "laundry", "family", "appliance", "front load"],
  },
  {
    id: "samsung-ecobubble-8kg",
    name: "EcoBubble 8kg",
    brand: "Samsung",
    category: "washing-machine",
    priceValue: 42990,
    rating: 4.5,
    aiScore: 87,
    availability: "In Stock",
    features: ["EcoBubble wash", "Digital inverter motor", "Hygiene steam", "Good smart diagnostics"],
    specs: [
      { label: "Type", value: "Front load" },
      { label: "Capacity", value: "8kg" },
      { label: "Motor", value: "Digital Inverter" },
      { label: "Programs", value: "12 wash programs" },
      { label: "Smart Features", value: "Smart Check" },
    ],
    pros: ["Efficient cleaning at lower temperatures", "Good value in front-load segment", "Useful hygiene modes"],
    cons: ["UI can feel busy", "Installation space needs attention"],
    bestFor: ["mid-size households", "energy-conscious laundry"],
    notRecommendedFor: ["very tight utility rooms", "buyers needing 9kg+ capacity"],
    tags: ["samsung", "washing machine", "laundry", "family", "appliance", "front load"],
  },
  {
    id: "ifb-senator-mxn-8012",
    name: "Senator MXN 8kg",
    brand: "IFB",
    category: "washing-machine",
    priceValue: 39990,
    rating: 4.4,
    aiScore: 85,
    availability: "Limited Stock",
    features: ["4D wash", "Cradle wash drum", "Aqua Energie", "Deep clean focus"],
    specs: [
      { label: "Type", value: "Front load" },
      { label: "Capacity", value: "8kg" },
      { label: "Motor", value: "High-efficiency motor" },
      { label: "Programs", value: "15 wash programs" },
      { label: "Special Mode", value: "Aqua Energie" },
    ],
    pros: ["Strong stain removal", "Good program variety", "Fabric care is solid"],
    cons: ["Service experience can vary", "Interface is less polished"],
    bestFor: ["stain-focused family laundry", "users wanting many programs"],
    notRecommendedFor: ["buyers preferring simple controls", "areas with limited service coverage"],
    tags: ["ifb", "washing machine", "laundry", "family", "appliance", "front load"],
  },
  {
    id: "bosch-serie-6-8kg",
    name: "Serie 6 8kg",
    brand: "Bosch",
    category: "washing-machine",
    priceValue: 44990,
    rating: 4.6,
    aiScore: 88,
    availability: "In Stock",
    features: ["EcoSilence drive", "Anti-vibration design", "Excellent build quality", "Water-efficient cycles"],
    specs: [
      { label: "Type", value: "Front load" },
      { label: "Capacity", value: "8kg" },
      { label: "Motor", value: "EcoSilence Drive" },
      { label: "Programs", value: "14 wash programs" },
      { label: "Noise Control", value: "Anti-vibration sidewall" },
    ],
    pros: ["Quiet during operation", "Strong build quality", "Good water efficiency"],
    cons: ["Premium pricing", "Cycles can take longer"],
    bestFor: ["quiet home laundry", "premium appliance buyers"],
    notRecommendedFor: ["quick wash only expectations", "lower-budget replacements"],
    tags: ["bosch", "washing machine", "laundry", "quiet", "appliance", "front load"],
  },
  {
    id: "whirlpool-stainwash-pro-9kg",
    name: "Stainwash Pro 9kg",
    brand: "Whirlpool",
    category: "washing-machine",
    priceValue: 36990,
    rating: 4.3,
    aiScore: 83,
    availability: "In Stock",
    features: ["Hard-water wash", "Large 9kg drum", "Stain-focused programs", "Value pricing"],
    specs: [
      { label: "Type", value: "Top load" },
      { label: "Capacity", value: "9kg" },
      { label: "Motor", value: "Inverter" },
      { label: "Programs", value: "12 wash programs" },
      { label: "Special Mode", value: "Hard Water Wash" },
    ],
    pros: ["Good value for large capacity", "Useful hard-water support", "Faster access with top load"],
    cons: ["Wash quality trails front loads", "Less premium finish"],
    bestFor: ["large families on a budget", "homes needing easy top-load access"],
    notRecommendedFor: ["best fabric care expectations", "very quiet laundry spaces"],
    tags: ["whirlpool", "washing machine", "laundry", "budget", "appliance", "top load"],
  },
  {
    id: "ps5-slim",
    name: "PlayStation 5 Slim",
    brand: "Sony",
    category: "gaming",
    priceValue: 54990,
    rating: 4.9,
    aiScore: 95,
    availability: "In Stock",
    features: ["Strong exclusives", "4K gaming", "Fast SSD load times", "Excellent controller feedback"],
    specs: [
      { label: "Platform", value: "Home console" },
      { label: "Storage", value: "1TB SSD" },
      { label: "Output", value: "Up to 4K 120Hz" },
      { label: "Ray Tracing", value: "Supported" },
      { label: "Included", value: "DualSense wireless controller" },
    ],
    pros: ["Excellent game library", "Fast and polished experience", "DualSense adds immersion"],
    cons: ["Online subscription costs extra", "Portable use is not possible"],
    bestFor: ["living room console gaming", "exclusive title fans"],
    notRecommendedFor: ["portable gaming needs", "mouse-keyboard-first preferences"],
    tags: ["ps5", "playstation", "gaming", "console", "sony", "4k"],
  },
  {
    id: "xbox-series-x",
    name: "Xbox Series X",
    brand: "Microsoft",
    category: "gaming",
    priceValue: 52990,
    rating: 4.8,
    aiScore: 93,
    availability: "In Stock",
    features: ["Powerful hardware", "Game Pass ecosystem", "Quick Resume", "4K gaming"],
    specs: [
      { label: "Platform", value: "Home console" },
      { label: "Storage", value: "1TB SSD" },
      { label: "Output", value: "Up to 4K 120Hz" },
      { label: "Ray Tracing", value: "Supported" },
      { label: "Ecosystem", value: "Xbox Game Pass" },
    ],
    pros: ["Outstanding value with Game Pass", "Excellent performance", "Quick Resume is genuinely useful"],
    cons: ["Fewer must-play exclusives", "Controller feels conservative next to DualSense"],
    bestFor: ["subscription-based gamers", "multi-platform households"],
    notRecommendedFor: ["exclusive-heavy PlayStation fans", "portable play expectations"],
    tags: ["xbox", "gaming", "console", "game pass", "4k", "microsoft"],
  },
  {
    id: "asus-rog-ally-x",
    name: "ROG Ally X",
    brand: "ASUS",
    category: "gaming",
    priceValue: 79990,
    rating: 4.6,
    aiScore: 90,
    availability: "Limited Stock",
    features: ["Handheld PC gaming", "Improved battery life", "Windows flexibility", "High-refresh display"],
    specs: [
      { label: "Platform", value: "Handheld gaming PC" },
      { label: "Chip", value: "AMD Ryzen Z1 Extreme" },
      { label: "Memory", value: "24GB LPDDR5X" },
      { label: "Storage", value: "1TB SSD" },
      { label: "Display", value: "7-inch FHD 120Hz" },
    ],
    pros: ["Portable access to PC games", "Battery improves over original", "Flexible Windows library"],
    cons: ["Windows handheld quirks remain", "Expensive for a secondary device"],
    bestFor: ["portable PC gaming", "enthusiasts with Steam libraries"],
    notRecommendedFor: ["simple console-like UI expectations", "tight gaming budgets"],
    tags: ["asus", "rog ally", "gaming", "handheld", "pc", "portable"],
  },
  {
    id: "lenovo-legion-go",
    name: "Legion Go",
    brand: "Lenovo",
    category: "gaming",
    priceValue: 74990,
    rating: 4.5,
    aiScore: 88,
    availability: "In Stock",
    features: ["Large handheld display", "Detachable controllers", "Versatile kickstand", "PC game compatibility"],
    specs: [
      { label: "Platform", value: "Handheld gaming PC" },
      { label: "Chip", value: "AMD Ryzen Z1 Extreme" },
      { label: "Memory", value: "16GB LPDDR5X" },
      { label: "Storage", value: "1TB SSD" },
      { label: "Display", value: "8.8-inch QHD+ 144Hz" },
    ],
    pros: ["Large immersive screen", "Kickstand and controllers add flexibility", "Good Steam library access"],
    cons: ["Heavy for long handheld sessions", "Battery life is only okay"],
    bestFor: ["large-screen handheld gaming", "travel-friendly PC gaming"],
    notRecommendedFor: ["ultra-light handheld preferences", "buyers wanting console simplicity"],
    tags: ["lenovo", "legion go", "gaming", "handheld", "pc", "portable"],
  },
  {
    id: "nintendo-switch-oled",
    name: "Switch OLED",
    brand: "Nintendo",
    category: "gaming",
    priceValue: 34990,
    rating: 4.7,
    aiScore: 87,
    availability: "In Stock",
    features: ["Portable hybrid gaming", "Great first-party library", "OLED display", "Easy couch multiplayer"],
    specs: [
      { label: "Platform", value: "Hybrid console" },
      { label: "Storage", value: "64GB internal" },
      { label: "Output", value: "1080p docked / 720p handheld" },
      { label: "Display", value: "7-inch OLED" },
      { label: "Battery", value: "4.5 to 9 hours" },
    ],
    pros: ["Excellent exclusive library", "Very flexible form factor", "Family-friendly multiplayer"],
    cons: ["Less powerful hardware", "No native 4K output"],
    bestFor: ["portable casual gaming", "family multiplayer"],
    notRecommendedFor: ["4K performance seekers", "competitive high-frame-rate gaming"],
    tags: ["nintendo", "switch", "gaming", "portable", "console", "family"],
  },
  {
    id: "ipad-air-m2",
    name: "iPad Air M2",
    brand: "Apple",
    category: "tablet",
    priceValue: 59900,
    rating: 4.8,
    aiScore: 94,
    availability: "In Stock",
    features: ["Powerful M2 chip", "Excellent app ecosystem", "Accessory support", "Great display quality"],
    specs: [
      { label: "Display", value: "11-inch Liquid Retina" },
      { label: "Chip", value: "Apple M2" },
      { label: "Storage", value: "128GB" },
      { label: "Accessory Support", value: "Apple Pencil Pro, Magic Keyboard" },
      { label: "Battery", value: "Up to 10 hours" },
    ],
    pros: ["Excellent performance headroom", "Best tablet app ecosystem", "Great accessories"],
    cons: ["Accessories cost extra", "iPadOS still limits some desktop workflows"],
    bestFor: ["students and creators", "portable media and note-taking"],
    notRecommendedFor: ["full laptop replacement for power users", "budget tablet shopping"],
    tags: ["ipad", "apple", "tablet", "student", "creator", "notes"],
  },
  {
    id: "samsung-galaxy-tab-s10",
    name: "Galaxy Tab S10",
    brand: "Samsung",
    category: "tablet",
    priceValue: 79999,
    rating: 4.7,
    aiScore: 92,
    availability: "Pre-order",
    features: ["Large AMOLED display", "S Pen included", "Strong multitasking", "DeX mode"],
    specs: [
      { label: "Display", value: "12.4-inch Dynamic AMOLED" },
      { label: "Chip", value: "Snapdragon 8 Gen series" },
      { label: "Storage", value: "256GB" },
      { label: "Accessory Support", value: "S Pen, keyboard cover" },
      { label: "Battery", value: "10,090mAh" },
    ],
    pros: ["Excellent display for media", "S Pen value is strong", "DeX adds desktop-like flexibility"],
    cons: ["Large size is less portable", "Android tablet apps vary in polish"],
    bestFor: ["multitasking and media", "Android tablet buyers"],
    notRecommendedFor: ["compact tablet preferences", "users wanting the best pro apps"],
    tags: ["samsung", "tablet", "android", "s pen", "media", "productivity"],
  },
  {
    id: "oneplus-pad-2",
    name: "Pad 2",
    brand: "OnePlus",
    category: "tablet",
    priceValue: 39999,
    rating: 4.5,
    aiScore: 88,
    availability: "In Stock",
    features: ["Strong performance", "Smooth large display", "Good battery", "Clean software"],
    specs: [
      { label: "Display", value: "12.1-inch 3K 144Hz" },
      { label: "Chip", value: "Snapdragon 8 Gen 3 class" },
      { label: "Storage", value: "256GB" },
      { label: "Accessory Support", value: "Keyboard and stylus" },
      { label: "Battery", value: "9,510mAh" },
    ],
    pros: ["Strong price-to-performance", "Smooth display experience", "Good battery endurance"],
    cons: ["Accessory ecosystem is smaller", "Tablet app ecosystem is less mature than iPad"],
    bestFor: ["value-focused Android tablets", "students consuming and creating content"],
    notRecommendedFor: ["best pro app needs", "compact handheld tablet use"],
    tags: ["oneplus", "tablet", "android", "budget", "student", "media"],
  },
  {
    id: "xiaomi-pad-6s-pro",
    name: "Pad 6S Pro",
    brand: "Xiaomi",
    category: "tablet",
    priceValue: 44999,
    rating: 4.4,
    aiScore: 86,
    availability: "In Stock",
    features: ["Large high-resolution display", "Fast charging", "Useful multitasking", "Competitive pricing"],
    specs: [
      { label: "Display", value: "12.4-inch 3K 144Hz" },
      { label: "Chip", value: "Snapdragon 8 Gen 2" },
      { label: "Storage", value: "256GB" },
      { label: "Charging", value: "120W fast charging" },
      { label: "Battery", value: "10,000mAh" },
    ],
    pros: ["Big display for the money", "Charging is very fast", "Good general performance"],
    cons: ["Software polish is uneven", "Accessory support is limited"],
    bestFor: ["large-screen tablet value", "media and light productivity"],
    notRecommendedFor: ["long software support expectations", "high-end creator apps"],
    tags: ["xiaomi", "tablet", "android", "budget", "media", "productivity"],
  },
  {
    id: "lenovo-tab-p12",
    name: "Tab P12",
    brand: "Lenovo",
    category: "tablet",
    priceValue: 28999,
    rating: 4.3,
    aiScore: 83,
    availability: "In Stock",
    features: ["Affordable large screen", "Good accessory bundle value", "Solid speakers", "Student-friendly pricing"],
    specs: [
      { label: "Display", value: "12.7-inch 3K" },
      { label: "Chip", value: "Dimensity 7050" },
      { label: "Storage", value: "128GB" },
      { label: "Accessory Support", value: "Optional pen and keyboard" },
      { label: "Battery", value: "10,200mAh" },
    ],
    pros: ["Large screen at a lower price", "Good for students and streaming", "Decent speakers"],
    cons: ["Performance is only mid-range", "Long-term updates are limited"],
    bestFor: ["students on a budget", "home streaming and notes"],
    notRecommendedFor: ["power multitasking", "premium stylus expectations"],
    tags: ["lenovo", "tablet", "budget", "student", "media", "notes"],
  },
  {
    id: "sony-a7-iv",
    name: "Alpha A7 IV",
    brand: "Sony",
    category: "camera",
    priceValue: 209990,
    rating: 4.9,
    aiScore: 96,
    availability: "In Stock",
    features: ["Excellent hybrid shooting", "Strong autofocus", "Reliable video features", "Great lens ecosystem"],
    specs: [
      { label: "Sensor", value: "33MP full-frame" },
      { label: "Video", value: "4K 60fps" },
      { label: "Stabilization", value: "5-axis IBIS" },
      { label: "Autofocus", value: "Real-time Eye AF" },
      { label: "Storage", value: "Dual card slots" },
    ],
    pros: ["Excellent all-rounder for photo and video", "Autofocus is highly reliable", "Huge lens ecosystem"],
    cons: ["Expensive body-only price", "Rolling shutter still exists in some cases"],
    bestFor: ["hybrid creators", "serious photography and video"],
    notRecommendedFor: ["casual point-and-shoot needs", "entry-level budgets"],
    tags: ["sony", "camera", "mirrorless", "video", "photography", "creator"],
  },
  {
    id: "canon-r6-mark-ii",
    name: "EOS R6 Mark II",
    brand: "Canon",
    category: "camera",
    priceValue: 219990,
    rating: 4.8,
    aiScore: 95,
    availability: "Limited Stock",
    features: ["Fast burst shooting", "Excellent Canon color", "Strong autofocus", "Good handheld video"],
    specs: [
      { label: "Sensor", value: "24.2MP full-frame" },
      { label: "Video", value: "4K 60fps oversampled" },
      { label: "Stabilization", value: "In-body image stabilization" },
      { label: "Autofocus", value: "Dual Pixel CMOS AF II" },
      { label: "Storage", value: "Dual card slots" },
    ],
    pros: ["Excellent autofocus and usability", "Great color science", "Very balanced hybrid camera"],
    cons: ["RF lenses can be expensive", "Resolution is lower than some rivals"],
    bestFor: ["event photography", "hybrid photo and video work"],
    notRecommendedFor: ["buyers wanting maximum megapixels", "budget-conscious beginners"],
    tags: ["canon", "camera", "mirrorless", "video", "photography", "creator"],
  },
  {
    id: "nikon-z6-iii",
    name: "Z6 III",
    brand: "Nikon",
    category: "camera",
    priceValue: 229990,
    rating: 4.8,
    aiScore: 94,
    availability: "Pre-order",
    features: ["Excellent EVF", "Strong dynamic range", "Good autofocus upgrade", "Solid video tools"],
    specs: [
      { label: "Sensor", value: "24.5MP full-frame" },
      { label: "Video", value: "6K RAW internal" },
      { label: "Stabilization", value: "5-axis IBIS" },
      { label: "Autofocus", value: "3D tracking AF" },
      { label: "Storage", value: "CFexpress + SD" },
    ],
    pros: ["Excellent EVF and handling", "Strong photo quality", "Improved autofocus makes it more competitive"],
    cons: ["Lens ecosystem is still growing", "Price is high for enthusiasts"],
    bestFor: ["enthusiast hybrid shooters", "users who value handling and EVF quality"],
    notRecommendedFor: ["entry-level creators", "buyers wanting the broadest lens catalog"],
    tags: ["nikon", "camera", "mirrorless", "video", "photography", "creator"],
  },
  {
    id: "fujifilm-x-s20",
    name: "X-S20",
    brand: "Fujifilm",
    category: "camera",
    priceValue: 129990,
    rating: 4.7,
    aiScore: 90,
    availability: "In Stock",
    features: ["Great color profiles", "Compact creator body", "Strong battery life", "Good autofocus"],
    specs: [
      { label: "Sensor", value: "26.1MP APS-C" },
      { label: "Video", value: "6.2K 30fps" },
      { label: "Stabilization", value: "7-stop IBIS" },
      { label: "Autofocus", value: "Subject-detection AF" },
      { label: "Screen", value: "Fully articulating" },
    ],
    pros: ["Excellent film simulations", "Compact but capable", "Very creator-friendly for travel"],
    cons: ["APS-C depth control differs from full frame", "Single card slot may limit some pros"],
    bestFor: ["travel creators", "photo-first videographers"],
    notRecommendedFor: ["high-end pro redundancy needs", "buyers wanting full-frame low-light output"],
    tags: ["fujifilm", "camera", "mirrorless", "travel", "creator", "photography"],
  },
  {
    id: "gopro-hero13-black",
    name: "Hero13 Black",
    brand: "GoPro",
    category: "camera",
    priceValue: 44990,
    rating: 4.5,
    aiScore: 86,
    availability: "In Stock",
    features: ["Action-ready durability", "Excellent stabilization", "Compact design", "Easy mounting options"],
    specs: [
      { label: "Sensor", value: "Action camera sensor" },
      { label: "Video", value: "5.3K 60fps" },
      { label: "Stabilization", value: "HyperSmooth" },
      { label: "Waterproofing", value: "Up to 10m" },
      { label: "Form Factor", value: "Action camera" },
    ],
    pros: ["Excellent stabilization", "Very compact and rugged", "Great for sports mounting"],
    cons: ["Low-light quality is limited", "Shorter battery in demanding modes"],
    bestFor: ["action sports", "travel clips and outdoor adventures"],
    notRecommendedFor: ["portrait photography", "studio-focused creators"],
    tags: ["gopro", "camera", "action", "travel", "video", "sports"],
  },
];

function buildSimilarityScore(source: Product, candidate: Product) {
  const sharedTags = candidate.tags.filter((tag) => source.tags.includes(tag)).length;
  const categoryBonus = candidate.category === source.category ? 24 : 0;
  const brandBonus = candidate.brand === source.brand ? 8 : 0;
  const ratingDistancePenalty = Math.abs(candidate.rating - source.rating) * 6;
  const aiScoreDistancePenalty = Math.abs(candidate.aiScore - source.aiScore) * 0.7;

  return sharedTags * 10 + categoryBonus + brandBonus - ratingDistancePenalty - aiScoreDistancePenalty;
}

function attachSimilarProducts(baseProducts: Product[], limit = 8): Product[] {
  return baseProducts.map((sourceProduct) => {
    const similarProductIds = baseProducts
      .filter((candidate) => candidate.id !== sourceProduct.id)
      .map((candidate) => ({
        id: candidate.id,
        score: buildSimilarityScore(sourceProduct, candidate),
      }))
      .sort((left, right) => right.score - left.score)
      .slice(0, limit)
      .map((entry) => entry.id);

    return {
      ...sourceProduct,
      similarProductIds,
    };
  });
}

export const products: Product[] = attachSimilarProducts(productSeeds.map(createProduct));

export function getProductById(id: string) {
  return products.find((product) => product.id === id);
}

export function getProductsByIds(ids: string[]) {
  const idSet = new Set(ids);
  return products.filter((product) => idSet.has(product.id));
}

export function getProductsByCategory(category: ProductCategory) {
  return products.filter((product) => product.category === category);
}

export function getFirstAvailableProduct(excludedId?: string) {
  return products.find((product) => product.id !== excludedId) ?? products[0];
}


