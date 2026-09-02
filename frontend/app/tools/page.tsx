import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Free Tools",
  description: "Practical online tools and calculators for business, finance, career and productivity.",
};

const PLANNED_TOOLS = [
  "Salary / Hike Calculator",
];

const BUSINESS_FINANCE_TOOLS = [
  { title: "Profit Margin Calculator", href: "/tools/profit-margin-calculator", description: "Calculate profit, profit margin and markup from cost and selling price." },
  { title: "Pricing Calculator", href: "/tools/pricing-calculator", description: "Find a selling price from your cost and desired profit margin." },
  { title: "Break-Even Calculator", href: "/tools/break-even-calculator", description: "Estimate the units and revenue needed to cover your costs." },
  { title: "Expense Calculator", href: "/tools/expense-calculator", description: "Organize business expenses and see totals by category." },
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
        <h2 className="lt-heading-2 mt-8">Business &amp; finance</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {BUSINESS_FINANCE_TOOLS.map((tool) => <Link key={tool.href} href={tool.href} className="block border border-[var(--border)] bg-[var(--surface-soft)] p-6 transition-colors hover:border-[var(--lt-accent)]"><h3 className="text-lg font-bold text-[var(--text-primary)]">{tool.title}</h3><p className="mt-3 text-sm leading-relaxed text-[var(--text-secondary)]">{tool.description}</p><span className="mt-5 inline-block text-sm font-bold text-[var(--lt-primary)]">Open tool &rarr;</span></Link>)}
        </div>
        <h2 className="lt-heading-2 mt-10">Business documents</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <Link href="/tools/invoice-generator" className="block border border-[var(--lt-primary)] bg-[var(--surface-soft)] p-6 transition-colors hover:border-[var(--lt-accent)]"><h3 className="text-lg font-bold text-[var(--text-primary)]">Invoice Generator</h3><p className="mt-3 text-sm leading-relaxed text-[var(--text-secondary)]">Create, review and print a professional invoice in INR.</p><span className="mt-5 inline-block text-sm font-bold text-[var(--lt-primary)]">Open generator &rarr;</span></Link>
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
