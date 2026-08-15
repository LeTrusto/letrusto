import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: [
          "/",
          "/shop",
          "/product",
          "/cart",
          "/about",
          "/contact",
          "/support",
          "/deals",
          "/shipping-policy",
          "/returns-policy",
          "/privacy-policy",
          "/terms-of-use",
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
