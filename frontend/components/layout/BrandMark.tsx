import Link from "next/link";

type Props = {
  compact?: boolean;
  footer?: boolean;
};

export default function BrandMark({ compact = false, footer = false }: Props) {
  return (
    <Link
      href="/"
      aria-label="LeTrusto home"
      className={`inline-flex shrink-0 items-center font-black tracking-[-0.04em] text-[var(--lt-primary)] ${compact ? "text-2xl" : footer ? "text-3xl text-white" : "text-4xl"}`}
    >
      LeTrusto
    </Link>
  );
}
