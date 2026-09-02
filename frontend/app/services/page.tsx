import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Digital Services",
  description: "Affordable digital help for websites, ecommerce, automation, integrations, dashboards and custom business tools.",
};

const SERVICES = [
  "Website setup",
  "Landing pages",
  "Business websites",
  "Ecommerce setup",
  "Website redesign",
  "WhatsApp and business integrations",
  "Automation",
  "Dashboards",
  "Custom business tools",
];

export default function ServicesPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-16 md:px-6 md:py-24">
      <div className="max-w-2xl">
        <p className="lt-eyebrow">LeTrusto Services</p>
        <h1 className="lt-heading-1 mt-3">Digital help with clear scope</h1>
        <p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">Tell us what you are trying to build or improve. We will understand the requirement first, then discuss a practical scope, timeline and price for the work involved.</p>
        <Link href="/support?tab=contact&category=contact" className="lt-btn lt-btn-md lt-btn-primary mt-8 inline-flex">Discuss a project</Link>
      </div>
      <section className="mt-14 border-t border-[var(--border)] pt-8">
        <h2 className="lt-heading-2">Areas we are preparing to support</h2>
        <ul className="mt-7 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {SERVICES.map((service) => <li key={service} className="border border-[var(--border)] bg-[var(--surface-soft)] px-4 py-4 text-sm font-semibold text-[var(--text-primary)]">{service}</li>)}
        </ul>
      </section>
    </main>
  );
}
