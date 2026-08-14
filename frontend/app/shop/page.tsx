import type { Metadata } from "next";
import ShopPageView from "./ShopPageView";

export const metadata: Metadata = {
  title: "Shop",
  description: "Browse trending beauty, jewellery, hair accessories, and style finds at everyday prices.",
};

export default function ShopPage() {
  return <ShopPageView />;
}
