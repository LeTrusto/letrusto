import Link from "next/link";
import Image from "next/image";

type Props = {
  compact?: boolean;
  footer?: boolean;
};

export default function BrandMark({ compact = false, footer = false }: Props) {
  const height = compact ? 40 : footer ? 48 : 56;
  const width = compact ? 140 : footer ? 160 : 200;
  const className = footer ? "brightness-0 invert" : "";

  return (
    <Link
      href="/"
      aria-label="LeTrusto home"
      className="inline-flex shrink-0 items-center"
    >
      <Image
        src="/images/logo/LeTrusto_Logo_Master_Transparent_300dpi.png"
        alt="LeTrusto"
        width={width}
        height={height}
        priority
        className={`h-auto w-auto ${className}`}
      />
    </Link>
  );
}
