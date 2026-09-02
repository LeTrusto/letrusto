import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

export default function DigitalProductCallout({ freelancer = false, clientWork = false }: { freelancer?: boolean; clientWork?: boolean }) {
  const product = clientWork
    ? { title: "Keep client work visible from lead to paid project.", description: "The Freelancer & Agency Client-Work Workbook connects scope, quotes, delivery, invoices, follow-up and profitability in one working flow.", slug: "freelancer-agency-client-work-workbook" }
    : freelancer
    ? { title: "Turn your rate into a repeatable quoting routine.", description: "The Freelancer Rate & Project Pricing Toolkit keeps targets, project buffers and monthly rate reviews together.", slug: "freelancer-rate-project-pricing-toolkit" }
    : { title: "Plan pricing and business finances in one place.", description: "The Small Business Finance & Pricing Toolkit turns quick calculations into a repeatable monthly planning routine.", slug: "small-business-finance-pricing-toolkit" };
  return <aside className="mt-16 border-l-4 border-[var(--lt-accent)] bg-[var(--surface-soft)] p-5 sm:p-6"><p className="lt-eyebrow">Go deeper</p><h2 className="mt-2 text-lg font-black text-[var(--text-primary)]">{product.title}</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">{product.description}</p><Link href={`/digital-products/${product.slug}`} className="lt-btn lt-btn-sm lt-btn-secondary mt-4">View the toolkit <ArrowUpRight size={15} aria-hidden="true" /></Link></aside>;
}