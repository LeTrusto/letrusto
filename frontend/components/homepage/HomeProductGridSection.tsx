import ProductCard from "@/components/ProductCard";
import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { Product } from "@/services/product.service";

type HomeProductGridSectionProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
  highlightLabel?: string;
  items: Product[];
};

export default function HomeProductGridSection({
  title,
  subtitle,
  ctaLabel,
  ctaHref,
  highlightLabel,
  items,
}: HomeProductGridSectionProps) {
  return (
    <section className="mx-auto mt-16 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} ctaLabel={ctaLabel} ctaHref={ctaHref} />
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {items.map((product) => (
          <ProductCard
            key={`${title}-${product.id}`}
            product={product}
            highlightLabel={highlightLabel}
          />
        ))}
      </div>
    </section>
  );
}
