import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms & Conditions",
  description: "Review the terms and conditions governing use of LeTrusto.",
  alternates: {
    canonical: "/terms-of-use",
  },
};

export default function TermsOfUsePage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-4xl font-black text-gray-900">Terms &amp; Conditions</h1>
      <p className="mt-3 text-sm text-gray-500">Last updated: 2026-08-31</p>

      <div className="mt-8 space-y-6 text-sm leading-7 text-gray-700">
        <section>
          <h2 className="text-lg font-bold text-gray-900">1. Platform Scope</h2>
          <p>LeTrusto provides free business tools, digital products delivered through authenticated downloads, productized services, and a separate storefront for made-to-order printed products. Free tools are informational utilities. A service enquiry is a request for discussion and a quote, not an order or completed purchase.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">2. Content and Availability</h2>
          <p>Prices, product availability, product options, production times, and shipping estimates for physical products may change. The details shown at checkout apply to your order. We may reject, cancel, or refund an order if a product, price, shipping rate, or checkout detail is unavailable or affected by an obvious error. Digital product prices and contents are shown before secure checkout, and verified purchases are linked to the customer account used for payment.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">3. Accounts</h2>
          <p>Email and password authentication is used for customer accounts. You are responsible for keeping your login details secure and for ensuring that your order, contact, and delivery information is accurate.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">4. Acceptable Use</h2>
          <p>Users must not misuse the platform, attempt unauthorized access, or abuse recommendation and support systems.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">5. Orders and Payment</h2>
          <p>India is the active purchasing destination for the physical storefront at this stage. International visitors may browse the storefront, but international checkout is currently unavailable. Active physical checkout payment is through Razorpay in INR. Service enquiries do not use physical checkout or create an order.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">6. Shipping, Cancellations, Returns, and Refunds</h2>
          <p>Shipping is charged separately from product price and is shown at checkout before payment. Because products are made to order, cancellation may only be possible before production or fulfillment begins. Returns and refunds are limited as described in the applicable policies.</p>
          <p className="mt-3">Please review the <Link className="underline" href="/shipping-policy">Shipping Policy</Link>, <Link className="underline" href="/cancellation-policy">Cancellation Policy</Link>, and <Link className="underline" href="/returns-policy">Returns &amp; Refunds Policy</Link>.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">7. Digital Products and Services</h2>
          <p>Digital products are editable files delivered through a protected download after payment is verified. Because access may begin immediately, digital purchases are generally non-refundable after download, except where required by applicable law or where LeTrusto cannot provide the purchased file. Service quotes are discussed and approved separately; submitting an enquiry does not authorize payment or begin work.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">8. Intellectual Property</h2>
          <p>LeTrusto branding, storefront content, product artwork, text, and site materials are owned by LeTrusto or used with permission. You may not copy, reproduce, or misuse site content except as allowed by law or with permission.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">9. Service Availability and Limits</h2>
          <p>We work to keep product information, checkout, and support available, but the service may be affected by maintenance, provider outages, internet issues, fulfillment delays, or other events outside our control. To the extent permitted by applicable law, LeTrusto is not responsible for indirect or consequential losses arising from use of the storefront.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">10. Policy Updates and Contact</h2>
          <p>We may update these Terms as the storefront, policies, or business operations change. For legal or policy questions, contact <a className="underline" href="mailto:hello@letrusto.com">hello@letrusto.com</a> or use the <Link className="underline" href="/support?tab=contact&category=contact">Support Centre</Link>.</p>
        </section>
      </div>
    </main>
  );
}
