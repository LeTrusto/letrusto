import type { Metadata } from "next";

import PhysicalCommercePaused from "@/components/commerce/PhysicalCommercePaused";

export const metadata: Metadata = {
  title: "Order details paused",
  robots: { index: false, follow: false },
};

export default function OrderDetailPage() {
  return <PhysicalCommercePaused area="Physical order details" />;
}
