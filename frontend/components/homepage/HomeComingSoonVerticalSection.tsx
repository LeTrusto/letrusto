import Link from "next/link";

import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { HomepageComingSoonItem } from "@/config/homepage";

type HomeComingSoonVerticalSectionProps = {
  title: string;
  item: HomepageComingSoonItem;
};

export default function HomeComingSoonVerticalSection({
  title,
  item,
}: HomeComingSoonVerticalSectionProps) {
  return (
    <section className="mx-auto mt-16 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle="Coming Soon" />

      <article className="relative overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm md:p-10">
        <div className="absolute -top-20 -right-16 h-56 w-56 rounded-full bg-cyan-100/70 blur-3xl" aria-hidden="true" />
        <div className="absolute -bottom-20 -left-16 h-56 w-56 rounded-full bg-violet-100/70 blur-3xl" aria-hidden="true" />

        <div className="relative z-10 grid gap-8 lg:grid-cols-[1.1fr_1fr] lg:items-center">
          <div>
            <div className="inline-flex rounded-2xl border border-slate-300 bg-slate-50 px-4 py-2 text-sm font-black tracking-[0.15em] text-slate-700">
              {item.illustration}
            </div>
            <h3 className="mt-4 text-3xl font-black tracking-tight text-slate-900 md:text-4xl">{item.title}</h3>
            <p className="mt-3 max-w-xl text-sm leading-relaxed text-slate-600 md:text-base">{item.description}</p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                href="/support?tab=contact&category=feedback"
                className="rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-5 py-3 text-sm font-bold text-white"
              >
                Notify Me
              </Link>
              <Link
                href="/ai"
                className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-500 hover:text-slate-900"
              >
                Ask AI
              </Link>
              <Link
                href="/"
                className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-500 hover:text-slate-900"
              >
                Return Home
              </Link>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">What You Can Expect</p>
            <ul className="mt-4 space-y-2.5 text-sm text-slate-700 md:text-base">
              {item.expectedItems.map((entry) => (
                <li key={`${item.id}-${entry}`} className="flex items-start gap-2.5">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-violet-600" />
                  <span>{entry}</span>
                </li>
              ))}
            </ul>
            <Link href={item.categoryHref} className="mt-5 inline-flex text-sm font-semibold text-violet-700 hover:text-violet-900">
              Open category page
            </Link>
          </div>
        </div>
      </article>
    </section>
  );
}
