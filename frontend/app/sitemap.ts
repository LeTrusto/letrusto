import type { MetadataRoute } from "next";

const BASE_URL = "https://letrusto.com";

const STATIC_ROUTES: MetadataRoute.Sitemap = [
  { url: `${BASE_URL}/`, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
  { url: `${BASE_URL}/compare`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
  { url: `${BASE_URL}/ai`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
  { url: `${BASE_URL}/search`, lastModified: new Date(), changeFrequency: "daily", priority: 0.9 },
  { url: `${BASE_URL}/deals`, lastModified: new Date(), changeFrequency: "daily", priority: 0.9 },
  { url: `${BASE_URL}/favorites`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.5 },
  { url: `${BASE_URL}/support`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.4 },
];

const CATEGORY_ROUTES: MetadataRoute.Sitemap = [
  "phone",
  "laptop",
  "headphones",
  "smartwatch",
  "television",
  "refrigerator",
  "washing-machine",
  "gaming",
  "tablet",
  "camera",
].map((slug) => ({
  url: `${BASE_URL}/search?category=${slug}`,
  lastModified: new Date(),
  changeFrequency: "weekly" as const,
  priority: 0.7,
}));

export default function sitemap(): MetadataRoute.Sitemap {
  return [...STATIC_ROUTES, ...CATEGORY_ROUTES];
}
