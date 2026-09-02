import type { Metadata } from "next";
import Link from "next/link";
import SchemaOrg from "@/components/SchemaOrg";
import ExpenseCalculator from "./ExpenseCalculator";

export const metadata: Metadata = { title: "Expense Calculator", description: "Organize and total business expenses by category in INR with a simple browser-based expense calculator.", alternates: { canonical: "/tools/expense-calculator" }, openGraph: { title: "Expense Calculator | LeTrusto", description: "Organize and total business expenses by category in INR.", url: "/tools/expense-calculator", siteName: "LeTrusto", type: "website" } };

export default function ExpenseCalculatorPage() {
  return <main className="mx-auto max-w-7xl px-4 py-12 md:px-6 md:py-20"><SchemaOrg type="WebPage" data={{ name: "Expense Calculator", url: "/tools/expense-calculator", description: "Organize and total business expenses by category." }} /><div className="max-w-3xl"><Link href="/tools" className="text-sm font-semibold text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">&larr; All tools</Link><p className="lt-eyebrow mt-8">Free organizer</p><h1 className="lt-heading-1 mt-3">Expense Calculator</h1><p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">List your business expenses, group them by category, and see the total at a glance.</p></div><div className="mt-10 md:mt-14"><ExpenseCalculator /></div><section className="mt-16 border-t border-[var(--border)] pt-12"><h2 className="lt-heading-2">Keep expense tracking simple</h2><p className="lt-body mt-4 max-w-2xl">Use consistent names and categories to make your totals easier to review. This calculator is a quick browser-based organizer, not an accounting system.</p></section></main>;
}
