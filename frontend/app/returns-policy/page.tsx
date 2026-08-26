import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Returns & Refunds",
  description: "LeTrusto returns and refund policy.",
};

export default function ReturnsPolicyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 md:px-6 py-10 md:py-16">
      <h1 className="lt-heading-1">Returns &amp; Refunds</h1>
      <div className="mt-6 lt-body space-y-4">
        <h2 className="lt-heading-3 mt-6">Return Window</h2>
        <p>Because our products are made to order, we do not accept returns for change of mind, incorrect size selection, or incorrect address details. Please review the product information and delivery address carefully before paying.</p>
        <h2 className="lt-heading-3 mt-6">Refund Process</h2>
        <p>If an item arrives damaged, defective, or materially different from the order, contact us within 7 days of delivery. After review, an approved refund or replacement will be arranged using the original payment method where applicable.</p>
        <h2 className="lt-heading-3 mt-6">Non-Returnable Items</h2>
        <p>Personalized, printed, and made-to-order items are not returnable unless they arrive damaged, defective, or incorrectly fulfilled.</p>
        <h2 className="lt-heading-3 mt-6">Contact</h2>
        <p>For return requests, please contact us through the Contact page.</p>
        <h2 className="lt-heading-3 mt-6">Return Review</h2>
        <p>We will review the request and confirm the next steps. Return shipping instructions, where applicable, will be provided after the request is accepted.</p>
      </div>
    </div>
  );
}
