import Image from "next/image";
import Link from "next/link";

type Props = {
  compact?: boolean;
  footer?: boolean;
};

export default function BrandMark({ compact = false, footer = false }: Props) {
  return (
    <Link href="/" aria-label="LeTrusto home" className="inline-flex shrink-0 items-center">
      {compact ? (
        <Image src="/letrusto-icon.svg" alt="LeTrusto" width={38} height={40} priority unoptimized className="h-10 w-auto" />
      ) : (
        <span className={footer ? "rounded-lg bg-[#fcfaf8] p-2" : ""}>
          <Image
            src="/LeTrusto%20Brand%20Logo.png"
            alt="LeTrusto - Discover. Choose. Trust."
            width={1774}
            height={887}
            priority
            unoptimized
            className={footer ? "h-auto w-48 sm:w-52" : "h-auto w-40 xl:w-44"}
          />
        </span>
      )}
    </Link>
  );
}
