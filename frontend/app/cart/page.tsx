import type { Metadata } from "next";
import PhysicalCommercePaused from "@/components/commerce/PhysicalCommercePaused";

export const metadata: Metadata = {
  title: "Cart",
  description: "Review your cart and proceed to checkout.",
  robots: { index: false, follow: false },
};

export default function CartPage() {
  return <PhysicalCommercePaused area="The cart" />;
}
