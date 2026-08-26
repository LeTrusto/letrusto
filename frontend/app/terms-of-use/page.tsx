import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Use",
  description: "Review the terms governing use of LeTrusto.",
  alternates: {
    canonical: "/terms-of-use",
  },
};

export default function TermsOfUsePage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-4xl font-black text-gray-900">Terms of Use</h1>
      <p className="mt-3 text-sm text-gray-500">Last updated: 2026-08-26</p>

      <div className="mt-8 space-y-6 text-sm leading-7 text-gray-700">
        <section>
          <h2 className="text-lg font-bold text-gray-900">1. Platform Scope</h2>
          <p>LeTrusto operates an online storefront for made-to-order printed products. Product images, colors, and measurements may vary slightly between screens, materials, and production batches.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">2. Content and Availability</h2>
          <p>Prices, product availability, production times, shipping estimates, and taxes may change. The details shown at checkout apply to your order. We may cancel and refund an order if a product or price is unavailable due to an obvious error.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">3. Acceptable Use</h2>
          <p>Users must not misuse the platform, attempt unauthorized access, or abuse recommendation and support systems.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">4. Contact</h2>
          <p>For legal or policy questions, please use /contact.</p>
        </section>
      </div>
    </main>
  );
}
