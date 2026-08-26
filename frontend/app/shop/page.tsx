import type { Metadata } from "next";
import ShopPageView from "./ShopPageView";

export const metadata: Metadata = {
  title: "Shop Unique Designs Printed On Demand",
  description: "Browse original apparel, wall art, accessories, home goods, and stationery shipped worldwide.",
  alternates: { canonical: "/shop" },
  openGraph: {
    title: "Shop Unique Designs Printed On Demand | LeTrusto",
    description: "Browse original apparel, wall art, accessories, home goods, and stationery shipped worldwide.",
    url: "/shop",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Shop Unique Designs Printed On Demand | LeTrusto",
    description: "Browse original apparel, wall art, accessories, home goods, and stationery shipped worldwide.",
    images: ["/images/og-default.svg"],
  },
};

export default function ShopPage() {
  return <ShopPageView />;
}
