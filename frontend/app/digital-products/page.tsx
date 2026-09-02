import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Digital Products",
  description: "Ready-to-use business templates, spreadsheets, dashboards and practical digital resources from LeTrusto.",
};

export default function DigitalProductsPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-16 md:px-6 md:py-24">
      <div className="max-w-2xl">
        <p className="lt-eyebrow">LeTrusto Digital Products</p>
        <h1 className="lt-heading-1 mt-3">Ready-to-use resources for real work</h1>
        <p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">The digital product library is being prepared with useful templates, spreadsheets, dashboards, kits and resources. Products and pricing will be published only when they are ready.</p>
      </div>
      <div className="mt-14 border border-[var(--border)] bg-[var(--surface-soft)] p-6 md:p-8">
        <h2 className="lt-heading-2">Coming soon</h2>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[var(--text-secondary)]">Business templates, freelancer and agency kits, creator resources, career templates, finance and productivity resources, and dashboards.</p>
      </div>
    </main>
  );
}
