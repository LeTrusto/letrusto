import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function NewsletterSignup() {
  return (
    <section className="py-16 md:py-20 bg-[var(--background)]">
      <div className="max-w-xl mx-auto px-4 md:px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-[var(--text-primary)] mb-2">Discover New Design Drops</h2>
        <p className="text-[var(--text-secondary)] font-medium">
          Fresh artwork and limited collections, printed when you order.
        </p>
        <Link href="/shop" className="lt-btn lt-btn-lg lt-btn-primary mt-8 inline-flex">
          Browse the shop
          <ArrowRight size={16} />
        </Link>
      </div>
    </section>
  );
}
