import type { Metadata } from "next";

import PhysicalCommercePaused from "@/components/commerce/PhysicalCommercePaused";

export const metadata: Metadata = {
  title: "Checkout paused",
  robots: { index: false, follow: false },
};

export default function CheckoutPage() {
  return <PhysicalCommercePaused area="Checkout" />;
}
