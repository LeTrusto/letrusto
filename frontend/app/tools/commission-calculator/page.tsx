import type { Metadata } from "next";
import Link from "next/link";
import SchemaOrg from "@/components/SchemaOrg";
import CommissionCalculator from "./CommissionCalculator";

export const metadata: Metadata = { title: "Commission Calculator", description: "Calculate commission and net amount from a sale or invoice amount and commission rate in INR.", alternates: { canonical: "/tools/commission-calculator" } };

export default function CommissionCalculatorPage() { return <main className="mx-auto max-w-7xl px-4 py-12 md:px-6 md:py-20"><SchemaOrg type="WebPage" data={{ name: "Commission Calculator", url: "/tools/commission-calculator", description: "Calculate commission and net amount from a sale or invoice amount and commission rate." }} /><div className="max-w-3xl"><Link href="/tools" className="text-sm font-semibold text-[var(--lt-primary)]">&larr; All tools</Link><p className="lt-eyebrow mt-8">Free calculator</p><h1 className="lt-heading-1 mt-3">Commission Calculator</h1><p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">Work out the commission amount and what remains from a sale, referral or invoice in INR.</p></div><div className="mt-10 md:mt-14"><CommissionCalculator /></div><section className="mt-16 border-t border-[var(--border)] pt-12"><h2 className="lt-heading-2">How to use it</h2><p className="lt-body mt-4 max-w-3xl">Enter the gross amount and agreed percentage. Use the result to review partner payouts, marketplace fees or sales commissions before recording the transaction.</p></section></main>; }
