import Link from "next/link";
import { ArrowRight } from "lucide-react";
import CommerceProductCard from "@/components/products/CommerceProductCard";
import type { CommerceProduct } from "@/types/commerce";

type Props = {
  title: string;
  subtitle?: string;
  products: CommerceProduct[];
  href?: string;
  ctaLabel?: string;
};

export default function ProductRail({ title, subtitle, products, href, ctaLabel }: Props) {
  return (
    <section className="py-10 md:py-14">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        <div className="flex items-end justify-between mb-6">
          <div>
            <h2 className="lt-heading-2">{title}</h2>
            {subtitle && <p className="mt-1 text-sm text-[var(--text-secondary)]">{subtitle}</p>}
          </div>
          {href && (
            <Link href={href} className="hidden sm:flex items-center gap-1 text-sm font-semibold text-[var(--text-primary)] hover:text-[var(--lt-accent-dark)] transition-colors">
              {ctaLabel ?? "View All"}
              <ArrowRight size={14} />
            </Link>
          )}
        </div>
        <div className="flex gap-4 overflow-x-auto pb-2 snap-x snap-mandatory scrollbar-hide">
          {products.map((product) => (
            <div key={product.id} className="snap-start shrink-0 w-[200px] sm:w-[220px] md:w-auto md:shrink md:flex-1 md:max-w-[260px]">
              <CommerceProductCard product={product} />
            </div>
          ))}
        </div>
        {href && (
          <div className="mt-4 sm:hidden text-center">
            <Link href={href} className="lt-btn lt-btn-md lt-btn-secondary">
              {ctaLabel ?? "View All"}
              <ArrowRight size={14} />
            </Link>
          </div>
        )}
      </div>
    </section>
  );
}
