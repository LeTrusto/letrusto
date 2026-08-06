import ProductCard from "@/components/ProductCard";
import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { HomeProductRailItem } from "@/services/homepage.service";

type HomeProductRailSectionProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
  items: HomeProductRailItem[];
  highlightLabel?: string;
};

export default function HomeProductRailSection({
  title,
  subtitle,
  ctaLabel,
  ctaHref,
  items,
  highlightLabel,
}: HomeProductRailSectionProps) {
  return (
    <section className="mx-auto mt-18 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} ctaLabel={ctaLabel} ctaHref={ctaHref} />
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {items.map((product, index) => (
          <ProductCard
            key={`${title}-${product.id}`}
            product={product}
            highlightLabel={highlightLabel}
            priority={index < 2}
          />
        ))}
      </div>
    </section>
  );
}
