import Link from "next/link";

import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import ProductCard from "@/components/ProductCard";
import type { Product } from "@/services/product.service";

type HomeDealsSpotlightSectionProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
  items: Product[];
};

export default function HomeDealsSpotlightSection({
  title,
  subtitle,
  ctaLabel,
  ctaHref,
  items,
}: HomeDealsSpotlightSectionProps) {
  if (items.length === 0) {
    return null;
  }

  const [heroDeal, ...otherDeals] = items;

  return (
    <section className="mx-auto mt-16 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} ctaLabel={ctaLabel} ctaHref={ctaHref} />
      <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
        <div className="rounded-3xl border border-amber-200 bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50 p-6 shadow-sm">
          <p className="inline-flex rounded-full bg-amber-500 px-3 py-1 text-xs font-bold text-white">Best Value Right Now</p>
          <h3 className="mt-4 text-2xl font-black tracking-tight text-slate-900">{heroDeal.name}</h3>
          <p className="mt-2 text-sm text-slate-600">{heroDeal.aiSummary}</p>
          <div className="mt-4 flex flex-wrap gap-2 text-xs font-semibold">
            <span className="rounded-full bg-slate-900 px-3 py-1 text-white">AI Score {heroDeal.aiScore}</span>
            <span className="rounded-full bg-white px-3 py-1 text-slate-800">{heroDeal.price}</span>
          </div>
          <div className="mt-6">
            <ProductCard product={heroDeal} highlightLabel="Deal" aiReason={heroDeal.aiSummary} />
          </div>
        </div>

        <div className="space-y-4">
          {otherDeals.slice(0, 3).map((deal) => (
            <article key={`deal-${deal.id}`} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h4 className="text-base font-bold text-slate-900">{deal.name}</h4>
                  <p className="mt-1 line-clamp-2 text-sm text-slate-600">{deal.aiSummary}</p>
                </div>
                <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">{deal.price}</span>
              </div>
              <p className="mt-2 text-xs font-semibold text-violet-700">AI Score {deal.aiScore}</p>
              <Link href={`/product/${deal.id}`} className="mt-3 inline-flex text-sm font-semibold text-slate-700 hover:text-violet-700">
                Explore deal
              </Link>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
