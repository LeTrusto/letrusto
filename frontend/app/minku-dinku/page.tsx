import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Minku & Dinku",
  description: "A future LeTrusto sub-brand for children's books, activities, worksheets and printables.",
};

export default function MinkuDinkuPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-16 md:px-6 md:py-24">
      <div className="max-w-2xl">
        <p className="lt-eyebrow">A LeTrusto sub-brand</p>
        <h1 className="lt-heading-1 mt-3">Minku &amp; Dinku</h1>
        <p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">A separate future home for children&apos;s books, activity packs, educational worksheets and printables.</p>
        <p className="mt-4 text-sm text-[var(--text-muted)]">This section is being prepared and is not available yet.</p>
      </div>
    </main>
  );
}
