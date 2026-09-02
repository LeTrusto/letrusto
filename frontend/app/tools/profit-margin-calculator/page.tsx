import type { Metadata } from "next";
import Link from "next/link";
import SchemaOrg from "@/components/SchemaOrg";
import ProfitMarginCalculator from "./ProfitMarginCalculator";

export const metadata: Metadata = {
  title: "Profit Margin Calculator",
  description: "Calculate profit, profit margin and markup from your cost and selling price in INR.",
  alternates: { canonical: "/tools/profit-margin-calculator" },
  openGraph: {
    title: "Profit Margin Calculator | LeTrusto",
    description: "Calculate profit, profit margin and markup from your cost and selling price in INR.",
    url: "/tools/profit-margin-calculator",
    siteName: "LeTrusto",
    type: "website",
  },
};

export default function ProfitMarginCalculatorPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-12 md:px-6 md:py-20">
      <SchemaOrg type="WebPage" data={{ name: "Profit Margin Calculator", url: "/tools/profit-margin-calculator", description: "Calculate profit, profit margin and markup from cost and selling price." }} />
      <div className="max-w-3xl">
        <Link href="/tools" className="text-sm font-semibold text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">&larr; All tools</Link>
        <p className="lt-eyebrow mt-8">Free calculator</p>
        <h1 className="lt-heading-1 mt-3">Profit Margin Calculator</h1>
        <p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">Find your profit, profit margin and markup from two simple numbers. Built for quick pricing checks in INR.</p>
      </div>

      <div className="mt-10 md:mt-14">
        <ProfitMarginCalculator />
      </div>

      <section className="mt-16 grid gap-10 border-t border-[var(--border)] pt-12 md:grid-cols-2 md:gap-14">
        <div>
          <h2 className="lt-heading-2">What is profit margin?</h2>
          <p className="lt-body mt-4">Profit margin is the percentage of the selling price that remains as profit after the cost is deducted. A higher margin means more of each sale remains after cost.</p>
          <h2 className="lt-heading-2 mt-10">Margin vs markup</h2>
          <p className="lt-body mt-4">Margin is calculated against the selling price. Markup is calculated against the cost. For example, a ₹60 cost and ₹100 selling price gives ₹40 profit, a 40% margin and a 66.67% markup.</p>
        </div>
        <div className="border border-[var(--border)] bg-[var(--surface-soft)] p-6 md:p-8">
          <h2 className="lt-heading-2">Formulas</h2>
          <div className="mt-5 space-y-4 font-mono text-sm text-[var(--text-primary)]">
            <p>Profit = Selling Price - Cost</p>
            <p>Profit Margin = (Profit / Selling Price) x 100</p>
            <p>Markup = (Profit / Cost) x 100</p>
          </div>
          <p className="mt-6 text-xs leading-relaxed text-[var(--text-muted)]">When cost or selling price is ₹0, the related percentage is shown as not available because division by zero is undefined.</p>
        </div>
      </section>
    </main>
  );
}
