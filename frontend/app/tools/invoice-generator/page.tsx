import type { Metadata } from "next";
import Link from "next/link";
import SchemaOrg from "@/components/SchemaOrg";
import InvoiceGenerator from "./InvoiceGenerator";

export const metadata: Metadata = {
  title: "Free Invoice Generator",
  description: "Create a professional invoice in INR with items, discounts, tax, notes and a print-to-PDF option.",
  alternates: { canonical: "/tools/invoice-generator" },
  openGraph: {
    title: "Free Invoice Generator | LeTrusto",
    description: "Create a professional invoice in INR with items, discounts, tax, notes and a print-to-PDF option.",
    url: "/tools/invoice-generator",
    siteName: "LeTrusto",
    type: "website",
  },
};

export default function InvoiceGeneratorPage() {
  return (
    <main className="invoice-page mx-auto max-w-7xl px-4 py-12 md:px-6 md:py-20">
      <SchemaOrg type="WebPage" data={{ name: "Free Invoice Generator", url: "/tools/invoice-generator", description: "Create a professional invoice in INR with items, discounts, tax and notes." }} />
      <div className="invoice-tool-controls max-w-3xl">
        <Link href="/tools" className="text-sm font-semibold text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">&larr; All tools</Link>
        <p className="lt-eyebrow mt-8">Free browser-based tool</p>
        <h1 className="lt-heading-1 mt-3">Invoice Generator</h1>
        <p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">Create, review and print a simple professional invoice in INR. Your invoice information stays in this browser and is not uploaded.</p>
      </div>

      <div className="mt-10 md:mt-14"><InvoiceGenerator /></div>

      <section className="invoice-tool-controls mt-16 grid gap-10 border-t border-[var(--border)] pt-12 md:grid-cols-2 md:gap-14">
        <div>
          <h2 className="lt-heading-2">How to create an invoice</h2>
          <ol className="mt-5 space-y-3 text-sm leading-relaxed text-[var(--text-secondary)]">
            <li><strong className="text-[var(--text-primary)]">1.</strong> Enter your business and customer details.</li>
            <li><strong className="text-[var(--text-primary)]">2.</strong> Add the products or services provided.</li>
            <li><strong className="text-[var(--text-primary)]">3.</strong> Apply a discount or tax if applicable.</li>
            <li><strong className="text-[var(--text-primary)]">4.</strong> Review the totals and print or save as PDF.</li>
          </ol>
        </div>
        <div>
          <h2 className="lt-heading-2">Invoice tips</h2>
          <p className="lt-body mt-4">Use a clear invoice number that you control, describe each item precisely, and confirm payment and tax details before sending the invoice.</p>
          <p className="mt-4 text-xs leading-relaxed text-[var(--text-muted)]">This tool is a practical document generator, not tax or legal advice. Verify applicable invoicing requirements for your situation.</p>
          <Link href="/tools/profit-margin-calculator" className="mt-6 inline-block text-sm font-bold text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">Check your profit margin &rarr;</Link>
        </div>
      </section>
    </main>
  );
}
