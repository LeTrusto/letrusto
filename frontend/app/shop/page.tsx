import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "Digital products coming soon",
  description: "LeTrusto is preparing practical digital tools, templates and services.",
  alternates: { canonical: "/shop" },
  robots: { index: false, follow: false },
};

export default function ShopPage() {
  return (
    <main className="flex min-h-[60vh] items-center justify-center px-4 py-20 text-center">
      <div className="max-w-xl">
        <p className="mb-4 text-sm font-bold uppercase tracking-[0.2em] text-[var(--lt-accent)]">LeTrusto</p>
        <h1 className="lt-heading-1">The digital shop is being prepared</h1>
        <p className="mt-4 text-[var(--text-secondary)]">
          Physical products are currently paused while we build tools, templates and services for Indian businesses.
        </p>
      </div>
    </main>
  );
}
