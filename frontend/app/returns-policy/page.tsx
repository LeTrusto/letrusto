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
        <p>Products may be returned within 7 days of delivery, provided they are unused and in original packaging.</p>
        <h2 className="lt-heading-3 mt-6">Refund Process</h2>
        <p>Refunds will be processed to the original payment method within 5–7 business days of receiving the returned item.</p>
        <h2 className="lt-heading-3 mt-6">Non-Returnable Items</h2>
        <p>Certain items such as earrings and personal care products may not be eligible for return due to hygiene reasons.</p>
        <h2 className="lt-heading-3 mt-6">Contact</h2>
        <p>For return requests, please contact us through the Contact page.</p>
        <h2 className="lt-heading-3 mt-6">Return Review</h2>
        <p>We will review the request and confirm the next steps. Return shipping instructions, where applicable, will be provided after the request is accepted.</p>
      </div>
    </div>
  );
}
