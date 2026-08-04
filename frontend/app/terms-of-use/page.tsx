import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Use — LeTrusto",
  description: "Review the terms governing use of LeTrusto.",
};

export default function TermsOfUsePage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-4xl font-black text-gray-900">Terms of Use</h1>
      <p className="mt-3 text-sm text-gray-500">Last updated: 2026-08-04</p>

      <div className="mt-8 space-y-6 text-sm leading-7 text-gray-700">
        <section>
          <h2 className="text-lg font-bold text-gray-900">1. Platform Scope</h2>
          <p>LeTrusto provides product discovery, comparison, editorial guides, and recommendation tools. We do not directly sell products.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">2. Content and Availability</h2>
          <p>Prices and specifications may change on retailer platforms. Always verify final details before purchase.</p>
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
