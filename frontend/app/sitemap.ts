import type { MetadataRoute } from "next";

import { MOCK_PRODUCTS } from "@/lib/mockData";
import { CATEGORY_MAP } from "@/types/commerce";

const BASE_URL = "https://letrusto.com";

const STATIC_ROUTES: MetadataRoute.Sitemap = [
  { url: `${BASE_URL}/`, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
  { url: `${BASE_URL}/shop`, lastModified: new Date(), changeFrequency: "daily", priority: 0.9 },
  { url: `${BASE_URL}/cart`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.5 },
  { url: `${BASE_URL}/deals`, lastModified: new Date(), changeFrequency: "daily", priority: 0.8 },
  { url: `${BASE_URL}/about`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.6 },
  { url: `${BASE_URL}/contact`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.5 },
  { url: `${BASE_URL}/support`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.4 },
  { url: `${BASE_URL}/shipping-policy`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.4 },
  { url: `${BASE_URL}/returns-policy`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.4 },
  { url: `${BASE_URL}/privacy-policy`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
  { url: `${BASE_URL}/terms-of-use`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
];

const CATEGORY_ROUTES: MetadataRoute.Sitemap = Object.keys(CATEGORY_MAP).map((slug) => ({
  url: `${BASE_URL}/shop?category=${slug}`,
  lastModified: new Date(),
  changeFrequency: "weekly" as const,
  priority: 0.8,
}));

const PRODUCT_ROUTES: MetadataRoute.Sitemap = MOCK_PRODUCTS.map((product) => ({
  url: `${BASE_URL}/product/${product.slug}`,
  lastModified: new Date(),
  changeFrequency: "weekly" as const,
  priority: 0.7,
}));

export default function sitemap(): MetadataRoute.Sitemap {
  return [...STATIC_ROUTES, ...CATEGORY_ROUTES, ...PRODUCT_ROUTES];
}

