import type { Metadata } from "next";

import PhysicalCommercePaused from "@/components/commerce/PhysicalCommercePaused";

export const metadata: Metadata = {
  title: "Fulfillment history paused",
  robots: { index: false, follow: false },
};

export default function FulfillmentHistoryPage() {
  return <PhysicalCommercePaused area="Physical fulfillment history" />;
}
