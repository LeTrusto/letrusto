import ProductCard from "@/components/ProductCard";
import HomeSectionHeader from "@/components/homepage/HomeSectionHeader";
import type { Product } from "@/services/product.service";

type HomeProductRailSectionProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
  highlightLabel?: string;
  items: Product[];
};

export default function HomeProductRailSection({
  title,
  subtitle,
  ctaLabel,
  ctaHref,
  highlightLabel,
  items,
}: HomeProductRailSectionProps) {
  return (
    <section className="mx-auto mt-16 w-full max-w-7xl px-6">
      <HomeSectionHeader title={title} subtitle={subtitle} ctaLabel={ctaLabel} ctaHref={ctaHref} />
      <div className="-mx-1 flex snap-x snap-mandatory gap-5 overflow-x-auto px-1 pb-3">
        {items.map((product) => (
          <div key={`${title}-${product.id}`} className="min-w-[280px] snap-start md:min-w-[320px] lg:min-w-[340px]">
            <ProductCard product={product} highlightLabel={highlightLabel} />
          </div>
        ))}
      </div>
    </section>
  );
}
