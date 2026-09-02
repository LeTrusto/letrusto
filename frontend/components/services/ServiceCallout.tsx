import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

export default function ServiceCallout() {
  return <aside className="mt-16 border-l-4 border-[var(--lt-primary)] bg-[var(--surface-soft)] p-5 sm:p-6"><p className="lt-eyebrow">Need something more tailored?</p><h2 className="mt-2 text-lg font-black text-[var(--text-primary)]">Explore practical digital services.</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">For a custom dashboard, website, automation or business tool, share the requirement and get a scoped next step.</p><Link href="/services" className="lt-btn lt-btn-sm lt-btn-secondary mt-4">Explore services <ArrowUpRight size={15} aria-hidden="true" /></Link></aside>;
}