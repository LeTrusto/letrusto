import type { Metadata } from "next";
import Link from "next/link";
import DigitalProductCallout from "@/components/digital-products/DigitalProductCallout";
import ServiceCallout from "@/components/services/ServiceCallout";
import DiscountCalculator from "./DiscountCalculator";

export const metadata: Metadata = { title: "Discount Calculator", description: "Calculate discount savings and final selling price from an original price in INR.", alternates: { canonical: "/tools/discount-calculator" } };

export default function DiscountCalculatorPage() { return <main className="mx-auto max-w-7xl px-4 py-12 md:px-6 md:py-20"><div className="max-w-3xl"><Link href="/tools" className="text-sm font-semibold text-[var(--lt-primary)]">&larr; All tools</Link><p className="lt-eyebrow mt-8">Free calculator</p><h1 className="lt-heading-1 mt-3">Discount Calculator</h1><p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">See the saving and final price when you apply a percentage discount to an INR price.</p></div><div className="mt-10 md:mt-14"><DiscountCalculator /></div><section className="mt-16 border-t border-[var(--border)] pt-12"><h2 className="lt-heading-2">Plan discounts clearly</h2><p className="lt-body mt-4 max-w-3xl">A discount changes the amount collected, so compare it with your costs and target margin before publishing an offer.</p></section><DigitalProductCallout /><ServiceCallout /></main>; }
