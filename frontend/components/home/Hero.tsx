import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Hero() {
  return (
    <section className="bg-[var(--background)] py-16 md:py-20 lg:py-24">
      <div className="max-w-[1280px] mx-auto px-4 md:px-6 text-center">
        <div className="mb-6 inline-block">
          <span className="text-sm font-bold tracking-widest text-[var(--lt-accent)] uppercase">OWN YOUR STYLE</span>
        </div>
        <h1 className="mb-6 text-5xl font-black leading-[1.08] tracking-tight text-[var(--text-primary)] sm:text-6xl md:text-6xl lg:text-7xl">
          YOUR DESIGN.<br />
          FRESHLY PRINTED.
        </h1>
        <p className="mx-auto mt-6 max-w-[680px] text-lg font-medium leading-relaxed text-[var(--text-secondary)]">
          Custom apparel, accessories and home decor — printed on demand and shipped worldwide.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Link href="/shop" className="lt-btn lt-btn-xl lt-btn-primary w-full sm:w-auto">
            SHOP DESIGNS
            <ArrowRight size={18} strokeWidth={2.5} />
          </Link>
          <Link href="/how-it-works" className="lt-btn lt-btn-xl lt-btn-secondary w-full sm:w-auto">
            HOW IT WORKS
          </Link>
        </div>
      </div>
    </section>
  );
}
