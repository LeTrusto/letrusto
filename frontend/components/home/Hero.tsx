import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Hero() {
  return (
    <section className="bg-[#f7f8ee]">
      <div className="max-w-7xl mx-auto px-4 md:px-6 py-12 md:py-20 text-center">
        <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black tracking-tight text-[var(--text-primary)] leading-[1.1]">
          YOUR DESIGN.<br />
          FRESHLY PRINTED.
        </h1>
        <p className="mt-4 md:mt-6 text-base md:text-lg text-[var(--text-secondary)] max-w-lg mx-auto">
          Custom apparel, accessories and home decor — printed on demand and shipped worldwide.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link href="/shop" className="lt-btn lt-btn-lg lt-btn-primary w-full sm:w-auto">
            SHOP DESIGNS
            <ArrowRight size={16} />
          </Link>
          <Link href="/how-it-works" className="lt-btn lt-btn-lg lt-btn-secondary w-full sm:w-auto">
            HOW IT WORKS
          </Link>
        </div>
      </div>
    </section>
  );
}
