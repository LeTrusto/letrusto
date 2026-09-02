import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Free Tools",
  description: "Practical online tools and calculators for business, finance, career and productivity.",
};

const PLANNED_TOOLS = [
  "Pricing Calculator",
  "Break-Even Calculator",
  "Expense Calculator",
  "Salary / Hike Calculator",
];

export default function ToolsPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-16 md:px-6 md:py-24">
      <div className="max-w-2xl">
        <p className="lt-eyebrow">LeTrusto Tools</p>
        <h1 className="lt-heading-1 mt-3">Free tools for practical work</h1>
        <p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">We are preparing a focused collection of calculators, generators and utilities for businesses, freelancers, creators and professionals.</p>
      </div>
      <section className="mt-14 border-t border-[var(--border)] pt-8">
        <p className="lt-eyebrow">Available now</p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Link href="/tools/profit-margin-calculator" className="block border border-[var(--border)] bg-[var(--surface-soft)] p-6 transition-colors hover:border-[var(--lt-accent)]">
            <h2 className="lt-heading-2">Profit Margin Calculator</h2>
            <p className="mt-3 text-sm leading-relaxed text-[var(--text-secondary)]">Calculate profit, profit margin and markup from your cost price and selling price.</p>
            <span className="mt-5 inline-block text-sm font-bold text-[var(--lt-primary)]">Open calculator &rarr;</span>
          </Link>
          <Link href="/tools/invoice-generator" className="block border border-[var(--lt-primary)] bg-[var(--surface-soft)] p-6 transition-colors hover:border-[var(--lt-accent)]">
            <h2 className="lt-heading-2">Invoice Generator</h2>
            <p className="mt-3 text-sm leading-relaxed text-[var(--text-secondary)]">Create, review and print a professional invoice in INR.</p>
            <span className="mt-5 inline-block text-sm font-bold text-[var(--lt-primary)]">Open generator &rarr;</span>
          </Link>
        </div>
      </section>
      <section className="mt-14 border-t border-[var(--border)] pt-8">
        <h2 className="lt-heading-2">Planned tools</h2>
        <p className="mt-3 text-sm text-[var(--text-secondary)]">These tools are planned, not available yet. We will publish each one when it is ready to use.</p>
        <ul className="mt-7 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {PLANNED_TOOLS.map((tool) => <li key={tool} className="border border-[var(--border)] bg-[var(--surface-soft)] px-4 py-4 text-sm font-semibold text-[var(--text-primary)]">{tool}</li>)}
        </ul>
      </section>
    </main>
  );
}
