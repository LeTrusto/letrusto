import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Returns & Refunds",
  description: "LeTrusto returns and refund policy.",
};

export default function ReturnsPolicyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 md:px-6 py-10 md:py-16">
      <h1 className="lt-heading-1">Returns &amp; Refunds</h1>
      <p className="mt-3 text-sm text-[var(--text-muted)]">Last updated: 2026-08-31</p>
      <div className="mt-6 lt-body space-y-4">
        <h2 className="lt-heading-3 mt-6">Made-to-order products</h2>
        <p>LeTrusto products are made to order. We do not accept returns or exchanges for change of mind, size selection, or incorrect address details entered by the customer. Please review the product information, selected variant, and delivery address carefully before paying.</p>
        <h2 className="lt-heading-3 mt-6">Refund Process</h2>
        <p>If an item arrives damaged, defective, materially different from the order, or incorrectly fulfilled, contact us within 7 days of delivery. Please include your order number and appropriate evidence such as clear photos of the issue.</p>
        <p>LeTrusto will review the claim. Depending on the outcome, LeTrusto may provide a replacement or a refund. If a replacement is unavailable, a refund may be provided.</p>
        <h2 className="lt-heading-3 mt-6">Non-Returnable Items</h2>
        <p>Personalized, printed, and made-to-order items are not returnable unless they arrive damaged, defective, or incorrectly fulfilled.</p>
        <h2 className="lt-heading-3 mt-6">Digital products</h2>
        <p>Digital products are currently preview-only. Checkout, payment, entitlement creation, and download access are not available, so there is no digital purchase or download to refund at this time. When digital sales are enabled, the applicable access and refund terms will be shown before payment.</p>
        <h2 className="lt-heading-3 mt-6">Services</h2>
        <p>Submitting a service enquiry does not create an order or payment obligation. Any separately agreed service scope, price, payment terms, and cancellation terms will be discussed before work begins.</p>
        <h2 className="lt-heading-3 mt-6">Refund Timing</h2>
        <p>After an approved refund or cancellation, LeTrusto generally initiates the applicable refund within approximately 5-7 business days where applicable. Your bank or payment provider may take additional time to process and credit the amount. Refunds are not instant and bank-credit timing cannot be guaranteed by LeTrusto.</p>
        <h2 className="lt-heading-3 mt-6">Contact</h2>
        <p>For return or refund requests, contact us through the <Link className="underline" href="/support?tab=contact&category=contact">Support Centre</Link> or email <a className="underline" href="mailto:hello@letrusto.com">hello@letrusto.com</a>.</p>
        <h2 className="lt-heading-3 mt-6">Return Review</h2>
        <p>We will review the request and confirm the next steps. Do not ship a product back unless LeTrusto provides return instructions. Return shipping requirements, where applicable, depend on the reviewed issue and fulfillment process.</p>
      </div>
    </div>
  );
}
