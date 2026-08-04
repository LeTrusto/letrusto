import Link from "next/link";
import { Sparkles } from "lucide-react";

import ProductCard from "@/components/ProductCard";
import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { Product } from "@/services/product.service";

type HomeAIPicksFeaturedSectionProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
  items: Product[];
};

function summarizeAiReason(summary: string) {
  const clean = summary.trim();
  if (clean.length <= 130) {
    return clean;
  }

  return `${clean.slice(0, 127)}...`;
}

export default function HomeAIPicksFeaturedSection({
  title,
  subtitle,
  ctaLabel,
  ctaHref,
  items,
}: HomeAIPicksFeaturedSectionProps) {
  if (items.length === 0) {
    return null;
  }

  const [lead, ...rest] = items;

  return (
    <section className="mx-auto mt-16 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} ctaLabel={ctaLabel} ctaHref={ctaHref} />

      <div className="grid gap-6 xl:grid-cols-[1.25fr_1fr]">
        <article className="rounded-3xl border border-violet-200 bg-gradient-to-br from-violet-900 via-indigo-900 to-slate-900 p-6 text-white shadow-2xl shadow-indigo-900/20">
          <p className="inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide">
            <Sparkles className="h-3.5 w-3.5" />
            AI Featured Pick
          </p>
          <h3 className="mt-4 text-2xl font-black tracking-tight md:text-3xl">{lead.name}</h3>
          <p className="mt-2 text-sm text-white/85">{lead.brand}</p>
          <p className="mt-4 text-sm leading-relaxed text-white/90">{summarizeAiReason(lead.aiSummary)}</p>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <span className="rounded-full bg-emerald-400/20 px-3 py-1 text-xs font-semibold text-emerald-200">AI Score {lead.aiScore}</span>
            <span className="rounded-full bg-white/15 px-3 py-1 text-xs font-semibold text-white">{lead.price}</span>
            <Link href={`/products/${lead.id}`} className="rounded-xl bg-white px-4 py-2 text-sm font-bold text-violet-700 transition hover:bg-violet-50">
              View details
            </Link>
          </div>
        </article>

        <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-1">
          {rest.slice(0, 3).map((product) => (
            <div key={`ai-pick-${product.id}`}>
              <ProductCard
                product={product}
                highlightLabel="AI Pick"
                aiReason={summarizeAiReason(product.aiSummary)}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
