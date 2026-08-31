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
          "/about",
          "/support",
          "/deals",
          "/shipping-policy",
          "/returns-policy",
          "/cancellation-policy",
          "/privacy-policy",
          "/terms-of-use",
        ],
        disallow: [
          "/dashboard",
          "/admin",
          "/account",
          "/cart",
          "/checkout",
          "/orders",
          "/favorites",
          "/notifications",
          "/login",
          "/register",
          "/search",
          "/api",
        ],
      },
    ],
    sitemap: "https://letrusto.com/sitemap.xml",
  };
}
