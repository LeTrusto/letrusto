import Link from "next/link";
import { ArrowRight, Calculator, FileSpreadsheet, Workflow } from "lucide-react";

const AREAS = [
  {
    icon: Calculator,
    eyebrow: "Free tools",
    title: "Solve practical problems quickly",
    description: "Calculators, generators and utilities for business, finance, career and everyday work.",
    href: "/tools",
    action: "Explore tools",
  },
  {
    icon: FileSpreadsheet,
    eyebrow: "Digital products",
    title: "Start with something ready to use",
    description: "Templates, spreadsheets, dashboards and resource kits built for real-world needs.",
    href: "/digital-products",
    action: "Browse products",
  },
  {
    icon: Workflow,
    eyebrow: "Digital services",
    title: "Get the right digital help",
    description: "Websites, ecommerce, automation, integrations and custom business tools with clear scope.",
    href: "/services",
    action: "Explore services",
  },
] as const;

const UPCOMING_TOOLS = [
  "Invoice Generator",
  "Profit Margin Calculator",
  "Pricing Calculator",
  "Break-Even Calculator",
  "Expense Calculator",
  "Salary / Hike Calculator",
];

const PRODUCT_CATEGORIES = [
  "Business templates",
  "Freelancer & agency kits",
  "Creator resources",
  "Career templates",
  "Finance & productivity",
  "Dashboards & spreadsheets",
];

const SERVICE_CATEGORIES = [
  "Website setup",
  "Landing pages",
  "Ecommerce setup",
  "Automation & integrations",
  "Dashboards",
  "Custom business tools",
];

export default function DigitalOverview() {
  return (
    <>
      <section className="border-y border-[var(--border)] bg-[var(--surface-soft)] py-16 md:py-20">
        <div className="mx-auto max-w-7xl px-4 md:px-6">
          <div className="max-w-2xl">
            <p className="lt-eyebrow">The LeTrusto platform</p>
            <h2 className="lt-heading-2 mt-3">One place for useful digital solutions</h2>
            <p className="mt-4 text-base leading-relaxed text-[var(--text-secondary)]">
              Start with a free tool, pick up a ready-made resource, or bring us a digital problem to solve.
            </p>
          </div>
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {AREAS.map((area) => {
              const Icon = area.icon;
              return (
                <article key={area.eyebrow} className="flex flex-col border border-[var(--border)] bg-[var(--background)] p-6 shadow-[0_4px_18px_rgba(60,35,100,0.04)]">
                  <Icon size={28} strokeWidth={1.8} className="text-[var(--lt-accent)]" />
                  <p className="mt-6 text-xs font-bold uppercase tracking-[0.16em] text-[var(--lt-accent)]">{area.eyebrow}</p>
                  <h3 className="mt-2 text-xl font-bold text-[var(--text-primary)]">{area.title}</h3>
                  <p className="mt-3 flex-1 text-sm leading-relaxed text-[var(--text-secondary)]">{area.description}</p>
                  <Link href={area.href} className="mt-6 inline-flex items-center gap-2 text-sm font-bold text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">
                    {area.action}
                    <ArrowRight size={16} />
                  </Link>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="py-16 md:py-20">
        <div className="mx-auto grid max-w-7xl gap-12 px-4 md:grid-cols-2 md:px-6">
          <div>
            <p className="lt-eyebrow">Coming next</p>
            <h2 className="lt-heading-2 mt-3">Tools for the decisions you make often</h2>
            <p className="mt-4 text-sm leading-relaxed text-[var(--text-secondary)]">
              The first tool collection is being planned around common business, finance and career workflows. These are planned utilities, not live products yet.
            </p>
            <Link href="/tools" className="lt-btn lt-btn-md lt-btn-primary mt-7 inline-flex">Explore tools <ArrowRight size={16} /></Link>
          </div>
          <ul className="grid content-start gap-3 sm:grid-cols-2">
            {UPCOMING_TOOLS.map((tool) => (
              <li key={tool} className="border-l-2 border-[var(--lt-accent)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)]">
                {tool === "Profit Margin Calculator" ? <Link href="/tools/profit-margin-calculator" className="text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">{tool}</Link> : tool === "Invoice Generator" ? <Link href="/tools/invoice-generator" className="text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">{tool}</Link> : tool}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="bg-[var(--surface-soft)] py-16 md:py-20">
        <div className="mx-auto grid max-w-7xl gap-12 px-4 md:grid-cols-2 md:px-6">
          <div>
            <p className="lt-eyebrow">Digital products</p>
            <h2 className="lt-heading-2 mt-3">Resources that help you move faster</h2>
            <p className="mt-4 text-sm leading-relaxed text-[var(--text-secondary)]">A future library of practical downloads is being shaped around these categories. No products or prices are being presented until they are ready.</p>
            <Link href="/digital-products" className="lt-btn lt-btn-md lt-btn-secondary mt-7 inline-flex">Browse digital products <ArrowRight size={16} /></Link>
          </div>
          <ul className="grid content-start gap-3 sm:grid-cols-2">
            {PRODUCT_CATEGORIES.map((category) => <li key={category} className="border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)]">{category}</li>)}
          </ul>
        </div>
      </section>

      <section className="py-16 md:py-20">
        <div className="mx-auto grid max-w-7xl gap-12 px-4 md:grid-cols-2 md:px-6">
          <div>
            <p className="lt-eyebrow">Digital services</p>
            <h2 className="lt-heading-2 mt-3">Practical help for your next project</h2>
            <p className="mt-4 text-sm leading-relaxed text-[var(--text-secondary)]">Bring a website, ecommerce, automation or dashboard requirement. Service scope and pricing will be discussed based on the actual work involved.</p>
            <Link href="/services" className="lt-btn lt-btn-md lt-btn-primary mt-7 inline-flex">Explore services <ArrowRight size={16} /></Link>
          </div>
          <ul className="grid content-start gap-3 sm:grid-cols-2">
            {SERVICE_CATEGORIES.map((category) => <li key={category} className="border-l-2 border-[var(--lt-primary)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)]">{category}</li>)}
          </ul>
        </div>
      </section>
    </>
  );
}
