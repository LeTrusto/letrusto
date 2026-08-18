import Image from "next/image";
import Link from "next/link";

type Props = {
  compact?: boolean;
};

export default function BrandMark({ compact = false }: Props) {
  return (
    <Link href="/" aria-label="LeTrusto home" className="inline-flex shrink-0 items-center">
      {compact ? (
        <Image src="/letrusto-icon.svg" alt="LeTrusto" width={30} height={32} priority unoptimized className="h-8 w-auto" />
      ) : (
        <Image
          src="/LeTrusto%20Brand%20Logo.png"
          alt="LeTrusto - Discover. Choose. Trust."
          width={1774}
          height={887}
          priority
          unoptimized
          className="h-auto w-36 sm:w-40"
        />
      )}
    </Link>
  );
}
