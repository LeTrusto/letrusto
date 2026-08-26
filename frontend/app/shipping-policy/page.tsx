import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Shipping Policy",
  description: "LeTrusto shipping information and delivery timelines.",
};

export default function ShippingPolicyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 md:px-6 py-10 md:py-16">
      <h1 className="lt-heading-1">Shipping Policy</h1>
      <div className="mt-6 lt-body space-y-4">
        <h2 className="lt-heading-3 mt-6">Delivery</h2>
        <p>Each product is made to order after purchase. Orders usually enter production within 2–5 business days, followed by delivery in approximately 5–15 business days depending on destination and carrier.</p>
        <h2 className="lt-heading-3 mt-6">Shipping Charges</h2>
        <p>Any applicable shipping charges are displayed at checkout before payment.</p>
        <h2 className="lt-heading-3 mt-6">Tracking</h2>
        <p>You will receive tracking information by email once your order has been produced and handed to the carrier. Tracking updates may take a few days to appear.</p>
        <h2 className="lt-heading-3 mt-6">Delivery Issues</h2>
        <p>If an order is delayed, lost, or arrives damaged, contact us through the Contact page with your order number and photographs where relevant. We will investigate with the fulfillment and delivery partners.</p>
      </div>
    </div>
  );
}
