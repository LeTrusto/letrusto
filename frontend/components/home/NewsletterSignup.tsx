import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function NewsletterSignup() {
  return (
    <section className="py-12 md:py-16 bg-[var(--surface-muted)]">
      <div className="max-w-xl mx-auto px-4 md:px-6 text-center">
        <h2 className="lt-heading-2">Explore New Finds</h2>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">
          Browse the latest beauty, jewellery and style finds in the shop.
        </p>
        <Link href="/shop" className="lt-btn lt-btn-md lt-btn-primary mt-6">
          Browse the shop
          <ArrowRight size={16} />
        </Link>
      </div>
    </section>
  );
}
