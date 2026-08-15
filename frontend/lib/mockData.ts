/**
 * Mock product data for development.
 * ALL data here is placeholder — no real products, reviews, or ratings.
 */
import type { CommerceProduct } from "@/types/commerce";

export const MOCK_PRODUCTS: CommerceProduct[] = [
  // ── Jewellery ─────────────────────────────────────────
  {
    id: "lt-001",
    slug: "layered-gold-chain-necklace",
    name: "Layered Gold-Tone Chain Necklace",
    description: "Delicate multi-layer chain necklace with adjustable clasp. Lightweight everyday wear with a premium finish.",
    price: 349,
    compareAtPrice: 599,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "jewellery",
    categoryLabel: "Jewellery",
    variants: [{ id: "v1", label: "Finish", options: ["Gold", "Silver", "Rose Gold"] }],
    availability: "in-stock",
    tags: ["trending", "layered", "necklace"],
    specs: [{ label: "Material", value: "Alloy with gold plating" }, { label: "Length", value: "42cm + 5cm extender" }, { label: "Weight", value: "18g" }],
    isTrending: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-002",
    slug: "statement-pearl-drop-earrings",
    name: "Statement Pearl Drop Earrings",
    description: "Elegant faux-pearl drop earrings with a modern geometric frame. Perfect for both casual and festive looks.",
    price: 249,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "jewellery",
    categoryLabel: "Jewellery",
    availability: "in-stock",
    tags: ["pearl", "earrings", "statement"],
    specs: [{ label: "Material", value: "Zinc alloy + faux pearl" }, { label: "Drop Length", value: "4.5cm" }],
    isNewDrop: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-003",
    slug: "adjustable-butterfly-ring-set",
    name: "Adjustable Butterfly Ring Set (3pc)",
    description: "Set of three dainty adjustable rings featuring butterfly and floral motifs. Stackable design.",
    price: 199,
    compareAtPrice: 349,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "jewellery",
    categoryLabel: "Jewellery",
    availability: "in-stock",
    tags: ["ring", "set", "butterfly", "adjustable"],
    isTrending: true,
    isLetrustoPick: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-004",
    slug: "bohemian-beaded-bracelet-stack",
    name: "Bohemian Beaded Bracelet Stack",
    description: "Colourful beaded bracelet set with natural stone-look beads. Set of 5 mix-and-match bracelets.",
    price: 279,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "jewellery",
    categoryLabel: "Jewellery",
    availability: "in-stock",
    tags: ["bracelet", "bohemian", "stack"],
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },

  // ── Hair & Style ──────────────────────────────────────
  {
    id: "lt-005",
    slug: "silk-scrunchie-set-pastel",
    name: "Silk Scrunchie Set — Pastel (6pc)",
    description: "Premium satin-finish scrunchies in pastel shades. Gentle on hair, zero-crease hold.",
    price: 199,
    compareAtPrice: 349,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "hair-style",
    categoryLabel: "Hair & Style",
    variants: [{ id: "v1", label: "Set", options: ["Pastel", "Neutral", "Bold"] }],
    availability: "in-stock",
    tags: ["scrunchie", "silk", "hair"],
    isTrending: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-006",
    slug: "claw-clip-large-matte",
    name: "Large Matte Claw Clip",
    description: "Oversized matte-finish claw clip for thick hair. Strong grip, lightweight design.",
    price: 149,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "hair-style",
    categoryLabel: "Hair & Style",
    variants: [{ id: "v1", label: "Colour", options: ["Black", "Brown", "Cream", "Sage"] }],
    availability: "in-stock",
    tags: ["claw clip", "hair", "matte"],
    isLetrustoPick: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-007",
    slug: "pearl-hair-pins-set",
    name: "Pearl Hair Pin Set (10pc)",
    description: "Elegant faux-pearl bobby pins for styling. Suitable for everyday and occasion wear.",
    price: 179,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "hair-style",
    categoryLabel: "Hair & Style",
    availability: "in-stock",
    tags: ["hair pin", "pearl", "styling"],
    isNewDrop: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },

  // ── Beauty Tools ──────────────────────────────────────
  {
    id: "lt-008",
    slug: "jade-roller-gua-sha-set",
    name: "Jade Roller & Gua Sha Set",
    description: "Natural jade stone roller and gua sha tool for facial massage. Comes in a velvet gift pouch.",
    price: 399,
    compareAtPrice: 699,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "beauty-tools",
    categoryLabel: "Beauty Tools",
    availability: "in-stock",
    tags: ["jade roller", "gua sha", "skincare"],
    isTrending: true,
    isLetrustoPick: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-009",
    slug: "makeup-brush-set-professional",
    name: "Professional Makeup Brush Set (12pc)",
    description: "Complete brush set with soft synthetic bristles. Includes foundation, contour, blush, eyeshadow, and blending brushes.",
    price: 449,
    compareAtPrice: 799,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "beauty-tools",
    categoryLabel: "Beauty Tools",
    variants: [{ id: "v1", label: "Colour", options: ["Black", "Pink", "White"] }],
    availability: "in-stock",
    tags: ["makeup", "brushes", "professional"],
    isNewDrop: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-010",
    slug: "led-makeup-mirror-compact",
    name: "LED Compact Mirror with Ring Light",
    description: "Portable folding mirror with built-in LED ring light. USB rechargeable, 3 brightness levels.",
    price: 349,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "beauty-tools",
    categoryLabel: "Beauty Tools",
    availability: "in-stock",
    tags: ["mirror", "LED", "compact"],
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },

  // ── Accessories ───────────────────────────────────────
  {
    id: "lt-011",
    slug: "minimalist-tote-bag-canvas",
    name: "Minimalist Canvas Tote Bag",
    description: "Sturdy canvas tote with magnetic snap closure. Internal pocket for phone/keys. Everyday essential.",
    price: 399,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "accessories",
    categoryLabel: "Accessories",
    variants: [{ id: "v1", label: "Colour", options: ["Natural", "Black", "Olive"] }],
    availability: "in-stock",
    tags: ["tote", "bag", "canvas", "minimalist"],
    isLetrustoPick: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-012",
    slug: "oversized-retro-sunglasses",
    name: "Oversized Retro Sunglasses",
    description: "UV400 protection, acetate-look frame. Vintage-inspired oversized design.",
    price: 299,
    compareAtPrice: 499,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "accessories",
    categoryLabel: "Accessories",
    variants: [{ id: "v1", label: "Colour", options: ["Black", "Tortoise", "Cream"] }],
    availability: "in-stock",
    tags: ["sunglasses", "retro", "UV400"],
    isTrending: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-013",
    slug: "satin-hair-scarf-printed",
    name: "Printed Satin Hair Scarf",
    description: "Versatile printed satin scarf — wear as headband, ponytail wrap, or bag accessory.",
    price: 179,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "accessories",
    categoryLabel: "Accessories",
    availability: "in-stock",
    tags: ["scarf", "satin", "printed"],
    isNewDrop: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },

  // ── Gifts ─────────────────────────────────────────────
  {
    id: "lt-014",
    slug: "aromatherapy-candle-set",
    name: "Aromatherapy Soy Candle Set (3pc)",
    description: "Hand-poured soy wax candles in Lavender, Vanilla, and Rose. Clean burn, no artificial dyes.",
    price: 499,
    compareAtPrice: 799,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "gifts",
    categoryLabel: "Gifts",
    availability: "in-stock",
    tags: ["candle", "aromatherapy", "gift set"],
    isTrending: true,
    isLetrustoPick: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-015",
    slug: "personalised-jewellery-box",
    name: "Velvet Jewellery Organiser Box",
    description: "Compact velvet-lined jewellery box with ring rolls, earring slots, and necklace compartments.",
    price: 449,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "gifts",
    categoryLabel: "Gifts",
    availability: "in-stock",
    tags: ["jewellery box", "organiser", "gift"],
    isNewDrop: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
  {
    id: "lt-016",
    slug: "self-care-gift-hamper",
    name: "Self-Care Gift Hamper",
    description: "Curated self-care kit: jade roller, satin scrunchies, scented candle, and compact mirror in a gift box.",
    price: 899,
    compareAtPrice: 1299,
    currency: "INR",
    images: ["/images/products/placeholder.svg"],
    category: "gifts",
    categoryLabel: "Gifts",
    bundleProducts: ["lt-008", "lt-005", "lt-014", "lt-010"],
    availability: "in-stock",
    tags: ["gift", "hamper", "self-care", "bundle"],
    isTrending: true,
    estimatedDelivery: "3-5 business days",
    returnInfo: "7-day easy returns",
  },
];

export function getMockProduct(slug: string): CommerceProduct | undefined {
  return MOCK_PRODUCTS.find((p) => p.slug === slug);
}

export function getMockProductById(id: string): CommerceProduct | undefined {
  return MOCK_PRODUCTS.find((p) => p.id === id);
}

export function getMockProductsByCategory(category: string): CommerceProduct[] {
  return MOCK_PRODUCTS.filter((p) => p.category === category);
}

export function getTrendingProducts(): CommerceProduct[] {
  return MOCK_PRODUCTS.filter((p) => p.isTrending);
}

export function getNewDrops(): CommerceProduct[] {
  return MOCK_PRODUCTS.filter((p) => p.isNewDrop);
}

export function getLetrustoPicks(): CommerceProduct[] {
  return MOCK_PRODUCTS.filter((p) => p.isLetrustoPick);
}

export function getProductsUnderPrice(maxPrice: number): CommerceProduct[] {
  return MOCK_PRODUCTS.filter((p) => p.price <= maxPrice);
}

export function getBundleProducts(): CommerceProduct[] {
  return MOCK_PRODUCTS.filter((p) => p.bundleProducts && p.bundleProducts.length > 0);
}
