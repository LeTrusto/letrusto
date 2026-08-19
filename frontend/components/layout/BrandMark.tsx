import Image from "next/image";
import Link from "next/link";

type Props = {
  compact?: boolean;
  footer?: boolean;
};

export default function BrandMark({ compact = false, footer = false }: Props) {
  const cropClass = footer
    ? "h-[118px] w-[320px]"
    : "h-[120px] w-[360px]";
  const imageClass = footer
    ? "absolute left-0 top-[-23px] h-auto w-[320px] max-w-none"
    : "absolute left-0 top-[-28px] h-auto w-[360px] max-w-none";

  return (
    <Link href="/" aria-label="LeTrusto home" className="inline-flex shrink-0 items-center">
      {compact ? (
        <Image src="/letrusto-icon.svg" alt="LeTrusto" width={44} height={46} priority unoptimized className="h-12 w-auto" />
      ) : (
        <span className={`${cropClass} relative block overflow-hidden rounded-lg ${footer ? "bg-[#fcfaf8] p-0 shadow-[0_3px_16px_rgba(0,0,0,0.16)]" : ""}`}>
          <Image
            src="/LeTrusto%20Brand%20Logo.png"
            alt="LeTrusto - Discover. Choose. Trust."
            width={1774}
            height={887}
            priority
            unoptimized
            className={imageClass}
          />
        </span>
      )}
    </Link>
  );
}
