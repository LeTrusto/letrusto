import Link from "next/link";

import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { HomeGuideSummary } from "@/services/homepage.service";

type HomeLatestGuidesSectionProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
  items: HomeGuideSummary[];
};

const CATEGORY_BADGE: Record<string, string> = {
  guide: "bg-blue-100 text-blue-700",
  comparison: "bg-violet-100 text-violet-700",
  review: "bg-amber-100 text-amber-700",
};

function formatBadge(category: string) {
  return category === "comparison"
    ? "Comparison"
    : category === "review"
      ? "Review"
      : "Guide";
}

export default function HomeLatestGuidesSection({
  title,
  subtitle,
  ctaLabel,
  ctaHref,
  items,
}: HomeLatestGuidesSectionProps) {
  if (items.length === 0) {
    return (
      <section className="mx-auto mt-16 w-full max-w-7xl px-6">
        <HomeSectionHeader title={title} subtitle={subtitle} ctaLabel={ctaLabel} ctaHref={ctaHref} />
        <div className="rounded-[1.75rem] border border-dashed border-slate-200 bg-white p-8 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Ready for content</p>
          <h3 className="mt-2 text-2xl font-black text-slate-900">AI tools buying guides are being curated</h3>
          <p className="mt-3 text-sm text-slate-600">Use Ask LeTrusto while we publish verified software buying guides.</p>
          <Link href="/ai" className="mt-5 inline-flex rounded-xl bg-slate-950 px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-800">
            Ask LeTrusto
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="mx-auto mt-16 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} ctaLabel={ctaLabel} ctaHref={ctaHref} />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {items.map((guide) => {
          const badgeClass = CATEGORY_BADGE[guide.category] ?? CATEGORY_BADGE.guide;
          return (
            <Link
              key={guide.slug}
              href={`/articles/${guide.slug}`}
              className="group rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm transition duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-lg"
            >
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${badgeClass}`}>
                {formatBadge(guide.category)}
              </span>
              <h3 className="mt-2.5 text-base font-bold leading-snug text-slate-900 group-hover:text-sky-700">
                {guide.title}
              </h3>
              <p className="mt-2 line-clamp-3 text-sm text-slate-600">{guide.excerpt}</p>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
