import Link from "next/link";
import Image from "next/image";

type Props = {
  compact?: boolean;
  footer?: boolean;
};

export default function BrandMark({ compact = false, footer = false }: Props) {
  const height = compact ? 48 : footer ? 48 : 64;
  const width = compact ? 160 : footer ? 160 : 200;
  const className = footer ? "brightness-0 invert" : "";

  return (
    <Link
      href="/"
      aria-label="LeTrusto home"
      className="inline-flex shrink-0 items-center justify-center"
    >
      <Image
        src="/images/logo/LeTrusto_Logo_Master_Transparent_300dpi.png"
        alt="LeTrusto"
        width={width}
        height={height}
        priority
        className={`w-auto h-auto ${className}`}
      />
    </Link>
  );
}
