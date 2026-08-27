import Link from "next/link";
import Image from "next/image";

type Props = {
  compact?: boolean;
  footer?: boolean;
};

export default function BrandMark({ compact = false, footer = false }: Props) {
  const width = compact ? 165 : footer ? 180 : 205;
  const height = Math.round(width * (1825 / 2795));

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
        className="object-contain"
      />
    </Link>
  );
}
