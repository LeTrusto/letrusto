import Link from "next/link";

type HomeSectionHeaderProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
};

export default function HomeSectionHeader({
  title,
  subtitle,
  ctaLabel,
  ctaHref,
}: HomeSectionHeaderProps) {
  return (
    <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h2 className="text-3xl font-black tracking-tight text-slate-950 md:text-4xl">{title}</h2>
        {subtitle ? <p className="mt-2 text-slate-600 md:text-base">{subtitle}</p> : null}
      </div>
      {ctaLabel && ctaHref ? (
        <Link
          href={ctaHref}
          className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:text-slate-900"
        >
          {ctaLabel}
        </Link>
      ) : null}
    </div>
  );
}
