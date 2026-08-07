import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Today's Deals",
  description: "Find curated deals, cashback offers, coupon codes, and AI-recommended savings.",
  alternates: {
    canonical: "/deals",
  },
  openGraph: {
    title: "Today's Deals",
    description: "Find curated deals, cashback offers, coupon codes, and AI-recommended savings.",
    url: "/deals",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Today's Deals",
    description: "Find curated deals, cashback offers, coupon codes, and AI-recommended savings.",
    images: ["/images/og-default.svg"],
  },
};

export { default } from "./DealsPage";
