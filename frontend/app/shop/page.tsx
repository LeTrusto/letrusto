import type { Metadata } from "next";
import ShopPageView from "./ShopPageView";

export const metadata: Metadata = {
  title: "Shop Beauty, Jewellery & Style Finds",
  description: "Browse trending beauty, jewellery, hair accessories, and style finds at everyday prices.",
  alternates: { canonical: "/shop" },
  openGraph: {
    title: "Shop Beauty, Jewellery & Style Finds | LeTrusto",
    description: "Browse trending beauty, jewellery, hair accessories, and style finds at everyday prices.",
    url: "/shop",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Shop Beauty, Jewellery & Style Finds | LeTrusto",
    description: "Browse trending beauty, jewellery, hair accessories, and style finds at everyday prices.",
    images: ["/images/og-default.svg"],
  },
};

export default function ShopPage() {
  return <ShopPageView />;
}
