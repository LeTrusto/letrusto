import type { Metadata } from "next";
import CartPageView from "./CartPageView";

export const metadata: Metadata = {
  title: "Cart",
  description: "Review your cart and proceed to checkout.",
  robots: { index: false, follow: false },
};

export default function CartPage() {
  return <CartPageView />;
}
