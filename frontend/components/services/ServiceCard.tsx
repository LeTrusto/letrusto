"use client";

import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { trackSafeEvent } from "@/lib/analytics";
import type { Service } from "@/types/services";

export default function ServiceCard({ service }: { service: Service }) {
  return <article className="lt-card lt-card-hover flex h-full flex-col"><p className="lt-eyebrow">{service.category}</p><h2 className="mt-3 text-xl font-black text-[var(--text-primary)]">{service.name}</h2><p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">{service.description}</p><div className="mt-5 border-l-2 border-[var(--lt-accent)] pl-4"><p className="text-xs font-bold uppercase tracking-wide text-[var(--text-muted)]">Typical use</p><p className="mt-1 text-sm leading-5 text-[var(--text-secondary)]">{service.useCase}</p></div><div className="mt-auto flex gap-4 pt-6"><Link href={`/services/${service.slug}`} className="lt-btn lt-btn-sm lt-btn-secondary">View scope <ArrowUpRight size={15} aria-hidden="true" /></Link><Link href={`/services/quote?service=${service.slug}`} onClick={() => trackSafeEvent("get_quote_clicked", { service_name: service.name, service_slug: service.slug, location: "service_card" })} className="self-center text-sm font-bold text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">Get a quote</Link></div></article>;
}