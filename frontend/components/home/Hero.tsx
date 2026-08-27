import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Hero() {
  return (
    <section className="bg-[var(--background)] py-20 md:py-32 lg:py-40">
      <div className="max-w-[1280px] mx-auto px-4 md:px-6 text-center">
        <div className="mb-6 inline-block">
          <span className="text-sm font-bold tracking-widest text-[var(--lt-accent)] uppercase">OWN YOUR STYLE</span>
        </div>
        <h1 className="text-5xl sm:text-6xl md:text-6xl lg:text-7xl font-black tracking-tight text-[var(--text-primary)] leading-[1.15] mb-8">
          YOUR DESIGN.<br />
          FRESHLY PRINTED.
        </h1>
        <p className="mt-8 text-lg text-[var(--text-secondary)] max-w-[680px] mx-auto font-medium leading-relaxed">
          Custom apparel, accessories and home decor — printed on demand and shipped worldwide.
        </p>
        <div className="mt-10 md:mt-12 flex flex-col sm:flex-row items-center justify-center gap-4">
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
