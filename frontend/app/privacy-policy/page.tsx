import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy — LeTrusto",
  description: "Read how LeTrusto collects, uses, and protects your data.",
};

export default function PrivacyPolicyPage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-4xl font-black text-gray-900">Privacy Policy</h1>
      <p className="mt-3 text-sm text-gray-500">Last updated: 2026-08-04</p>

      <div className="mt-8 space-y-6 text-sm leading-7 text-gray-700">
        <section>
          <h2 className="text-lg font-bold text-gray-900">1. Information We Collect</h2>
          <p>We collect account details you provide, product interaction data, and analytics events required to improve recommendations and platform reliability.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">2. How We Use Data</h2>
          <p>Data is used to personalize recommendations, improve search and compare workflows, prevent abuse, and support operational troubleshooting.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">3. Third-Party Services</h2>
          <p>LeTrusto uses trusted service providers for hosting, analytics, and authentication. These providers process data only as needed to operate the platform.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">4. Contact</h2>
          <p>Questions about privacy can be sent through our support channel at /contact.</p>
        </section>
      </div>
    </main>
  );
}
