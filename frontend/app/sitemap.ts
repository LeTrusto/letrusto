import type { MetadataRoute } from "next";

import { SITE_URL } from "@/config/site";

const BASE_URL = SITE_URL;

const STATIC_ROUTES: MetadataRoute.Sitemap = [
  { url: `${BASE_URL}/`, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  return STATIC_ROUTES;
}

