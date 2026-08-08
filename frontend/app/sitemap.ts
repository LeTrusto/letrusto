import type { MetadataRoute } from "next";

import { CATALOG_TREE } from "@/constants/index";
import { getAllProducts } from "@/services/product.service";

const BASE_URL = "https://letrusto.com";

const STATIC_ROUTES: MetadataRoute.Sitemap = [
  { url: `${BASE_URL}/`, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
  { url: `${BASE_URL}/ai-tools`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
  { url: `${BASE_URL}/articles`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
  { url: `${BASE_URL}/categories`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.85 },
  { url: `${BASE_URL}/guides`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.85 },
  { url: `${BASE_URL}/compare`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
  { url: `${BASE_URL}/ai`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
  { url: `${BASE_URL}/deals`, lastModified: new Date(), changeFrequency: "daily", priority: 0.9 },
  { url: `${BASE_URL}/search`, lastModified: new Date(), changeFrequency: "daily", priority: 0.7 },
  { url: `${BASE_URL}/support`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.4 },
  { url: `${BASE_URL}/contact`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.45 },
  { url: `${BASE_URL}/privacy-policy`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
  { url: `${BASE_URL}/terms-of-use`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
  { url: `${BASE_URL}/about`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.5 },
];

const CATEGORY_SLUGS = Array.from(
  new Set(
    CATALOG_TREE.flatMap((group) => {
      const nested = (group.children ?? []).map((child) => child.slug);
      return [group.slug, ...nested];
    })
  )
);

const CATEGORY_ROUTES: MetadataRoute.Sitemap = CATEGORY_SLUGS.map((slug) => ({
  url: `${BASE_URL}/category/${slug}`,
  lastModified: new Date(),
  changeFrequency: "weekly" as const,
  priority: 0.8,
}));

// 10 launch articles
const ARTICLE_ROUTES: MetadataRoute.Sitemap = [
  "best-web-hosting-india-2026",
  "hostinger-vs-bluehost-india",
  "best-phone-under-20000-india-2026",
  "best-laptop-for-students-india-2026",
  "canva-pro-vs-free-2026",
  "semrush-vs-ahrefs-india-2026",
  "best-vpn-for-india-2026",
  "iphone-16-pro-vs-samsung-s25-ultra",
  "best-ai-tools-developers-india-2026",
  "how-ai-helps-choose-right-product",
].map((slug) => ({
  url: `${BASE_URL}/articles/${slug}`,
  lastModified: new Date(),
  changeFrequency: "monthly" as const,
  priority: 0.75,
}));

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const products = await getAllProducts();
  const productRoutes: MetadataRoute.Sitemap = products.map((product) => ({
    url: `${BASE_URL}/products/${product.id}`,
    lastModified: new Date(),
    changeFrequency: "weekly",
    priority: 0.7,
  }));

  return [...STATIC_ROUTES, ...CATEGORY_ROUTES, ...ARTICLE_ROUTES, ...productRoutes];
}

