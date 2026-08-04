import { CheckCircle2 } from "lucide-react";

import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { TrustSignal } from "@/config/homepage";

type HomeTrustSignalsSectionProps = {
  title: string;
  subtitle?: string;
  items: TrustSignal[];
};

export default function HomeTrustSignalsSection({
  title,
  subtitle,
  items,
}: HomeTrustSignalsSectionProps) {
  return (
    <section className="mx-auto mt-16 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {items.map((item) => (
          <article
            key={item.id}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <CheckCircle2 className="h-5 w-5 text-emerald-600" aria-hidden="true" />
            <h3 className="mt-3 text-base font-bold text-slate-900">{item.title}</h3>
            <p className="mt-2 text-sm text-slate-600">{item.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
