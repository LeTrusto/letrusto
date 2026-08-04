import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "About LeTrusto",
  description: "Learn about LeTrusto and our mission to help people buy smarter.",
};

export default function AboutPage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-4xl font-black text-gray-900">About LeTrusto</h1>
      <p className="mt-4 text-gray-600">
        LeTrusto is an AI-powered buying advisor built for India. We help people compare products, understand trade-offs, and choose with confidence.
      </p>

      <div className="mt-8 space-y-6 text-sm leading-7 text-gray-700">
        <section>
          <h2 className="text-lg font-bold text-gray-900">What We Do</h2>
          <p>We combine structured product data, editorial guidance, and recommendation workflows to simplify buying decisions.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">How We Sustain the Platform</h2>
          <p>LeTrusto may earn commission from affiliate links. This does not change our commitment to transparent and useful recommendations.</p>
        </section>
      </div>

      <div className="mt-10 flex flex-wrap gap-3">
        <Link href="/guides" className="rounded-xl bg-purple-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-purple-700">Read Buying Guides</Link>
        <Link href="/support" className="rounded-xl border border-gray-200 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50">Contact Support</Link>
      </div>
    </main>
  );
}
