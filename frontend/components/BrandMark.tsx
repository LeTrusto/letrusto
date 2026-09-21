import Link from "next/link";

// Temporary neutral brand mark until the Bangalore Property brand is finalized.
export default function BrandMark() {
  return (
    <Link href="/" className="inline-flex items-center gap-2 text-lg font-black text-[var(--text-primary)]">
      Bangalore Property Platform
    </Link>
  );
}
