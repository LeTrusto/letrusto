import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

export default function DigitalProductCallout() {
  return <aside className="mt-16 border-l-4 border-[var(--lt-accent)] bg-[var(--surface-soft)] p-5 sm:p-6"><p className="lt-eyebrow">Go deeper</p><h2 className="mt-2 text-lg font-black text-[var(--text-primary)]">Plan pricing and business finances in one place.</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">The Small Business Finance &amp; Pricing Toolkit turns quick calculations into a repeatable monthly planning routine.</p><Link href="/digital-products/small-business-finance-pricing-toolkit" className="lt-btn lt-btn-sm lt-btn-secondary mt-4">View the toolkit <ArrowUpRight size={15} aria-hidden="true" /></Link></aside>;
}