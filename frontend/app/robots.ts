import type { MetadataRoute } from "next";
import { SITE_URL } from "@/config/site";

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
          "/shipping-policy",
          "/returns-policy",
          "/cancellation-policy",
          "/privacy-policy",
          "/terms-of-use",
          "/tools",
          "/digital-products",
          "/services",
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
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
