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
        <p className="text-sm font-semibold text-[var(--lt-rose)]">
          [DRAFT — requires final legal / operations review before publishing]
        </p>
        <h2 className="lt-heading-3 mt-6">Delivery</h2>
        <p>Orders are typically dispatched within 24–48 hours and delivered within 3–7 business days depending on your location.</p>
        <h2 className="lt-heading-3 mt-6">Shipping Charges</h2>
        <p>Shipping charges, if applicable, will be displayed at checkout before payment.</p>
        <h2 className="lt-heading-3 mt-6">Tracking</h2>
        <p>You will receive tracking information via email/SMS once your order is dispatched.</p>
      </div>
    </div>
  );
}
