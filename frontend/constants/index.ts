import type { CatalogBrandEntry, CatalogCategoryNode, CatalogSubcategoryBrands } from "@/types/catalog";

// ── Top-level catalog tree (mirrors DB hierarchy) ─────────────────────────────
export const CATALOG_TREE: CatalogCategoryNode[] = [
  {
    name: "Electronics",
    slug: "electronics",
    icon: "💻",
    children: [
      { name: "Smartphones", slug: "smartphones", icon: "📱" },
      { name: "Laptops & Ultrabooks", slug: "laptop", icon: "💻" },
      { name: "Tablets & iPads", slug: "tablet", icon: "📲" },
      { name: "Earbuds & TWS", slug: "earbuds-tws", icon: "🎧" },
      { name: "Headphones", slug: "headphones", icon: "🎵" },
      { name: "Smartwatches & Bands", slug: "smartwatch", icon: "⌚" },
      { name: "Cameras", slug: "camera", icon: "📷" },
      { name: "Televisions", slug: "television", icon: "📺" },
      { name: "Gaming", slug: "gaming", icon: "🎮" },
      { name: "Bluetooth Speakers", slug: "bluetooth-speakers", icon: "🔊" },
      { name: "Monitors", slug: "monitors-displays", icon: "🖥️" },
    ],
  },
  {
    name: "Home & Kitchen",
    slug: "home-kitchen",
    icon: "🏠",
    children: [
      { name: "Refrigerators", slug: "refrigerator", icon: "🧊" },
      { name: "Washing Machines", slug: "washing-machine", icon: "🫧" },
      { name: "Air Conditioners", slug: "air-conditioners", icon: "❄️" },
      { name: "Microwave Ovens", slug: "microwave-ovens", icon: "📡" },
    ],
  },
  { name: "Beauty", slug: "beauty", icon: "✨", children: [] },
  { name: "Baby Care", slug: "baby-care", icon: "👶", children: [] },
  { name: "Pet Care", slug: "pet-care", icon: "🐾", children: [] },
  { name: "Fitness", slug: "fitness", icon: "💪", children: [] },
  { name: "Furniture", slug: "furniture", icon: "🪑", children: [] },
];

// ── Brand catalog per sub-category ────────────────────────────────────────────
export const BRAND_CATALOG: CatalogSubcategoryBrands[] = [
  {
    subcategorySlug: "smartphones",
    subcategoryName: "Smartphones",
    brands: [
      {
        name: "Apple",
        slug: "apple",
        series: [
          "iPhone 16 Pro Max",
          "iPhone 16 Pro",
          "iPhone 16 Plus",
          "iPhone 16",
          "iPhone 15 Pro Max",
          "iPhone 15 Pro",
          "iPhone 15 Plus",
          "iPhone 15",
          "iPhone SE (3rd Gen)",
        ],
      },
      {
        name: "Samsung",
        slug: "samsung",
        series: [
          "Galaxy S25 Ultra",
          "Galaxy S25+",
          "Galaxy S25",
          "Galaxy Z Fold 6",
          "Galaxy Z Flip 6",
          "Galaxy A55",
          "Galaxy A35",
          "Galaxy M55",
          "Galaxy M35",
          "Galaxy F55",
        ],
      },
      {
        name: "OnePlus",
        slug: "oneplus",
        series: [
          "OnePlus 13",
          "OnePlus 12R",
          "OnePlus Nord 4",
          "OnePlus Nord CE 4",
          "OnePlus Nord CE 4 Lite",
          "OnePlus Open",
        ],
      },
      {
        name: "Google",
        slug: "google",
        series: [
          "Pixel 9 Pro XL",
          "Pixel 9 Pro",
          "Pixel 9",
          "Pixel 9 Pro Fold",
          "Pixel 8a",
        ],
      },
      {
        name: "Nothing",
        slug: "nothing",
        series: ["Nothing Phone (2a) Plus", "Nothing Phone (2a)", "Nothing Phone (2)"],
      },
      {
        name: "Motorola",
        slug: "motorola",
        series: [
          "Edge 50 Pro",
          "Edge 50 Ultra",
          "Edge 50 Fusion",
          "Moto G85",
          "Moto G64",
          "Razr 50 Ultra",
        ],
      },
      {
        name: "Xiaomi",
        slug: "xiaomi",
        series: [
          "Xiaomi 14 Ultra",
          "Xiaomi 14",
          "Redmi Note 14 Pro+",
          "Redmi Note 14 Pro",
          "Redmi Note 14",
          "Redmi 14C",
        ],
      },
      {
        name: "Realme",
        slug: "realme",
        series: [
          "Realme GT 6",
          "Realme GT 6T",
          "Realme Narzo 70 Pro",
          "Realme 13 Pro+",
          "Realme 13 Pro",
          "Realme C65",
        ],
      },
      {
        name: "OPPO",
        slug: "oppo",
        series: ["Find X8 Pro", "Find X8", "Reno 13 Pro", "Reno 13", "A3 Pro"],
      },
      {
        name: "Vivo",
        slug: "vivo",
        series: ["X200 Pro", "X200", "V40 Pro", "V40", "T3 Pro", "Y300 Pro"],
      },
      {
        name: "iQOO",
        slug: "iqoo",
        series: ["iQOO 13", "iQOO 12", "iQOO Neo 9 Pro", "iQOO Z9 Pro", "iQOO Z9"],
      },
      {
        name: "Honor",
        slug: "honor",
        series: ["Honor Magic 6 Pro", "Honor 200 Pro", "Honor 200", "Honor X9b"],
      },
    ],
  },
  {
    subcategorySlug: "laptop",
    subcategoryName: "Laptops & Ultrabooks",
    brands: [
      {
        name: "Apple",
        slug: "apple",
        series: [
          "MacBook Pro 16 M4 Max",
          "MacBook Pro 14 M4 Pro",
          "MacBook Air 15 M3",
          "MacBook Air 13 M3",
          "MacBook Pro 14 M3",
        ],
      },
      {
        name: "Dell",
        slug: "dell",
        series: [
          "XPS 15",
          "XPS 13",
          "Inspiron 16 5000",
          "Alienware m18",
          "Latitude 7450",
        ],
      },
      {
        name: "HP",
        slug: "hp",
        series: ["Spectre x360 14", "Envy x360 15", "EliteBook 840", "Omen 16", "Pavilion 15"],
      },
      {
        name: "Lenovo",
        slug: "lenovo",
        series: [
          "ThinkPad X1 Carbon",
          "Yoga 9i",
          "IdeaPad Slim 5",
          "Legion Pro 5i",
          "LOQ 15",
        ],
      },
      {
        name: "ASUS",
        slug: "asus",
        series: [
          "ZenBook 14 OLED",
          "VivoBook 15",
          "ROG Zephyrus G14",
          "ROG Strix G16",
          "ProArt Studiobook 16",
        ],
      },
      {
        name: "Microsoft",
        slug: "microsoft",
        series: ["Surface Pro 11", "Surface Laptop 7", "Surface Book 3"],
      },
      {
        name: "Acer",
        slug: "acer",
        series: ["Swift 14 AI", "Predator Helios 16", "Aspire 5", "Nitro 16"],
      },
      {
        name: "Samsung",
        slug: "samsung",
        series: ["Galaxy Book4 Pro 360", "Galaxy Book4 Pro", "Galaxy Book4 Edge"],
      },
    ],
  },
  {
    subcategorySlug: "tablet",
    subcategoryName: "Tablets",
    brands: [
      {
        name: "Apple",
        slug: "apple",
        series: [
          "iPad Pro 13 M4",
          "iPad Pro 11 M4",
          "iPad Air 13 M2",
          "iPad Air 11 M2",
          "iPad mini 7",
          "iPad 10th Gen",
        ],
      },
      {
        name: "Samsung",
        slug: "samsung",
        series: [
          "Galaxy Tab S10 Ultra",
          "Galaxy Tab S10+",
          "Galaxy Tab S10",
          "Galaxy Tab S10 FE",
          "Galaxy Tab A9+",
        ],
      },
      {
        name: "OnePlus",
        slug: "oneplus",
        series: ["OnePlus Pad 2", "OnePlus Pad Go"],
      },
      {
        name: "Xiaomi",
        slug: "xiaomi",
        series: ["Xiaomi Pad 7", "Xiaomi Pad 6s Pro", "Redmi Pad Pro"],
      },
      {
        name: "Realme",
        slug: "realme",
        series: ["Realme Pad X", "Realme Pad 2"],
      },
    ],
  },
  {
    subcategorySlug: "headphones",
    subcategoryName: "Headphones",
    brands: [
      {
        name: "Sony",
        slug: "sony",
        series: ["WH-1000XM6", "WH-1000XM5", "WF-1000XM5", "LinkBuds S"],
      },
      {
        name: "Bose",
        slug: "bose",
        series: ["QuietComfort Ultra Headphones", "QuietComfort 45", "SoundLink Max"],
      },
      {
        name: "Apple",
        slug: "apple",
        series: ["AirPods Pro 2", "AirPods 4", "AirPods Max"],
      },
      {
        name: "Samsung",
        slug: "samsung",
        series: ["Galaxy Buds3 Pro", "Galaxy Buds3", "Galaxy Buds FE"],
      },
      {
        name: "Sennheiser",
        slug: "sennheiser",
        series: ["Momentum 4 Wireless", "Momentum True Wireless 4"],
      },
      {
        name: "JBL",
        slug: "jbl",
        series: ["Tour One M2", "Live 770NC", "Tune 770NC", "Quantum 910 Wireless"],
      },
    ],
  },
  {
    subcategorySlug: "smartwatch",
    subcategoryName: "Smartwatches",
    brands: [
      {
        name: "Apple",
        slug: "apple",
        series: ["Apple Watch Series 10", "Apple Watch Ultra 2", "Apple Watch SE 2"],
      },
      {
        name: "Samsung",
        slug: "samsung",
        series: ["Galaxy Watch 7", "Galaxy Watch Ultra", "Galaxy Watch FE"],
      },
      {
        name: "Garmin",
        slug: "garmin",
        series: ["Fenix 8 AMOLED", "Forerunner 965", "Venu 3", "Instinct 3"],
      },
      {
        name: "Fitbit",
        slug: "fitbit",
        series: ["Sense 3", "Versa 4", "Charge 6"],
      },
      {
        name: "OnePlus",
        slug: "oneplus",
        series: ["OnePlus Watch 2", "OnePlus Watch 2R"],
      },
      {
        name: "Noise",
        slug: "noise",
        series: ["Noise ColorFit Pro 6", "Noise ColorFit Caliber 3"],
      },
    ],
  },
  {
    subcategorySlug: "camera",
    subcategoryName: "Cameras",
    brands: [
      {
        name: "Sony",
        slug: "sony",
        series: ["Alpha 7 IV", "Alpha 7C II", "Alpha ZV-E10 II", "ZV-1 II"],
      },
      {
        name: "Canon",
        slug: "canon",
        series: ["EOS R8", "EOS R50", "EOS R6 Mark II", "PowerShot V10"],
      },
      {
        name: "Nikon",
        slug: "nikon",
        series: ["Z6 III", "Z50 II", "Zfc", "Z30"],
      },
      {
        name: "Fujifilm",
        slug: "fujifilm",
        series: ["X-T5", "X100VI", "X-S20", "GFX 50S II"],
      },
      {
        name: "GoPro",
        slug: "gopro",
        series: ["HERO13 Black", "HERO12 Black", "MAX 360"],
      },
    ],
  },
  {
    subcategorySlug: "gaming",
    subcategoryName: "Gaming",
    brands: [
      {
        name: "Sony",
        slug: "sony",
        series: ["PlayStation 5 Slim", "PlayStation 5", "PlayStation VR2"],
      },
      {
        name: "Microsoft",
        slug: "microsoft",
        series: ["Xbox Series X", "Xbox Series S"],
      },
      {
        name: "Nintendo",
        slug: "nintendo",
        series: ["Nintendo Switch OLED", "Nintendo Switch Lite", "Nintendo Switch 2"],
      },
      {
        name: "ASUS",
        slug: "asus",
        series: ["ROG Ally X", "ROG Ally"],
      },
      {
        name: "Valve",
        slug: "valve",
        series: ["Steam Deck OLED", "Steam Deck"],
      },
    ],
  },
];

// ── Flat brand list derived from catalog ──────────────────────────────────────
export const ALL_BRANDS: string[] = [
  ...new Set(BRAND_CATALOG.flatMap((sc) => sc.brands.map((b) => b.name))),
].sort();

// ── Category label maps ───────────────────────────────────────────────────────
export const CATEGORY_LABELS: Record<string, string> = {
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
  electronics: "Electronics",
  "home-kitchen": "Home & Kitchen",
  hosting: "Hosting",
  saas: "SaaS",
  kitchen: "Kitchen",
  beauty: "Beauty",
  "baby-care": "Baby Care",
  "pet-care": "Pet Care",
  fitness: "Fitness",
  furniture: "Furniture",
  smartphones: "Smartphones",
  "laptops-ultrabooks": "Laptops & Ultrabooks",
  "tablets-ipads": "Tablets & iPads",
  "earbuds-tws": "Earbuds & TWS",
  "smartwatches-bands": "Smartwatches & Bands",
  "digital-cameras": "Cameras",
  "bluetooth-speakers": "Bluetooth Speakers",
  "monitors-displays": "Monitors & Displays",
  "televisions-oleds": "Televisions",
};

export function getCategoryLabel(slug: string): string {
  return CATEGORY_LABELS[slug] ?? slug;
}

// ── Get brands for a given subcategory slug ───────────────────────────────────
export function getBrandsForCategory(categorySlug: string): CatalogBrandEntry[] {
  return BRAND_CATALOG.find((sc) => sc.subcategorySlug === categorySlug)?.brands ?? [];
}

// ── Get all series for a brand across all categories ─────────────────────────
export function getSeriesForBrand(brandName: string): string[] {
  return BRAND_CATALOG.flatMap((sc) =>
    sc.brands.filter((b) => b.name.toLowerCase() === brandName.toLowerCase()).flatMap((b) => b.series)
  );
}
