"use client";

import Link from "next/link";
import { ArrowUpRight, FileSpreadsheet } from "lucide-react";
import { trackSafeEvent } from "@/lib/analytics";
import { formatDigitalProductPrice } from "@/lib/digitalProducts";
import type { DigitalProduct } from "@/types/digital-products";

export default function DigitalProductCard({ product }: { product: DigitalProduct }) {
  return (
    <article className="lt-card lt-card-hover flex h-full flex-col overflow-hidden p-0">
      <div className="border-b border-[var(--border)] bg-[#e8f1ee] p-5">
        <div className="flex aspect-[16/10] flex-col justify-between border border-[#b8cec5] bg-[#f7fbf8] p-4 shadow-sm">
          <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-[0.12em] text-[#28604e]"><span>LeTrusto workbook</span><FileSpreadsheet size={16} aria-hidden="true" /></div>
          <div><p className="text-xs font-semibold text-[#28604e]">{product.previewLabel}</p><p className="mt-1 text-xl font-black text-[#173c32]">{product.slug === "freelancer-agency-client-work-workbook" ? "Client-work lifecycle" : product.slug === "freelancer-rate-project-pricing-toolkit" ? "Rate &amp; quote planning" : "Finance &amp; pricing"}</p></div>
          <div className="grid grid-cols-3 gap-2 text-[10px] font-semibold text-[#28604e]"><span className="border border-[#b8cec5] bg-white p-2">{product.slug === "freelancer-agency-client-work-workbook" ? "Leads" : product.slug === "freelancer-rate-project-pricing-toolkit" ? "Rates" : "Pricing"}</span><span className="border border-[#b8cec5] bg-white p-2">{product.slug === "freelancer-agency-client-work-workbook" ? "Quotes" : product.slug === "freelancer-rate-project-pricing-toolkit" ? "Projects" : "Expenses"}</span><span className="border border-[#b8cec5] bg-white p-2">{product.slug === "freelancer-agency-client-work-workbook" ? "Payments" : product.slug === "freelancer-rate-project-pricing-toolkit" ? "Review" : "Break-even"}</span></div>
        </div>
      </div>
      <div className="flex flex-1 flex-col p-6"><p className="text-xs font-bold uppercase tracking-[0.12em] text-[var(--lt-accent-dark)]">{product.category.name}</p><h2 className="mt-3 text-xl font-black text-[var(--text-primary)]">{product.name}</h2><p className="mt-3 flex-1 text-sm leading-6 text-[var(--text-secondary)]">{product.description}</p><div className="mt-6 flex items-center justify-between gap-4"><div><p className="text-lg font-black text-[var(--text-primary)]">{formatDigitalProductPrice(product)}</p><p className="mt-1 text-xs text-[var(--text-muted)]">One-time purchase</p></div><Link href={`/digital-products/${product.slug}`} onClick={() => trackSafeEvent("digital_product_cta_clicked", { product_name: product.name, product_slug: product.slug, interaction: "view_product" })} className="lt-btn lt-btn-sm lt-btn-secondary">View product <ArrowUpRight size={15} aria-hidden="true" /></Link></div></div>
    </article>
  );
}