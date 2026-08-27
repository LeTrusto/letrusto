import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Hero() {
  return (
    <section className="bg-[var(--background)] py-16 md:py-28 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 md:px-6 text-center">
        <div className="mb-6 inline-block">
          <span className="text-sm md:text-base font-bold tracking-widest text-[var(--lt-accent)] uppercase">OWN YOUR STYLE</span>
        </div>
        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black tracking-tight text-[var(--text-primary)] leading-[1.1] mb-6">
          YOUR DESIGN.<br />
          FRESHLY PRINTED.
        </h1>
        <p className="mt-6 md:mt-8 text-lg md:text-xl text-[var(--text-secondary)] max-w-2xl mx-auto font-medium">
          Custom apparel, accessories and home decor — printed on demand and shipped worldwide.
        </p>
        <div className="mt-10 md:mt-14 flex flex-col sm:flex-row items-center justify-center gap-4">
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
