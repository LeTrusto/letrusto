import Link from "next/link";
import Image from "next/image";

type Props = {
  compact?: boolean;
  footer?: boolean;
  tone?: "light" | "dark";
};

export default function BrandMark({ compact = false, footer = false, tone = "dark" }: Props) {
  const isLight = tone === "light" || footer;
  const logoSource = compact ? "/favicon-192x192.png" : isLight ? "/logo-dark.png" : "/logo.png";

  return (
    <Link
      href="/"
      aria-label="LeTrusto home"
      className={`inline-flex shrink-0 items-center gap-3 ${isLight ? "text-white" : "text-slate-900"}`}
    >
      <Image
        src={logoSource}
        alt="LeTrusto"
        width={compact ? 192 : 2020}
        height={compact ? 192 : 778}
        priority={!compact}
        className={compact ? "h-9 w-9 object-contain" : "h-auto w-[150px] object-contain sm:w-[178px]"}
      />
    </Link>
  );
}
