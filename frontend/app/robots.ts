import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: [
          "/",
          "/about",
          "/affiliate-disclosure",
          "/methodology",
          "/ai-tools",
          "/articles",
          "/categories",
          "/category",
          "/compare",
          "/deals",
          "/guides",
          "/products",
          "/search",
          "/support",
        ],
        disallow: [
          "/dashboard",
          "/favorites",
          "/notifications",
          "/login",
          "/register",
          "/api",
        ],
      },
    ],
    sitemap: "https://letrusto.com/sitemap.xml",
  };
}
