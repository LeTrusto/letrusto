import ProductCard from "@/components/ProductCard";
import { products } from "@/lib/products";

function SectionHeading({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  return (
    <div className="mb-6 flex items-end justify-between gap-4">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-gray-900 md:text-4xl">{title}</h2>
        <p className="mt-2 text-gray-500">{subtitle}</p>
      </div>
    </div>
  );
}

function ProductRail({
  title,
  subtitle,
  items,
  highlightLabel,
}: {
  title: string;
  subtitle: string;
  items: typeof products;
  highlightLabel: string;
}) {
  return (
    <section className="mt-16">
      <SectionHeading title={title} subtitle={subtitle} />
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {items.map((product) => (
          <ProductCard key={`${title}-${product.id}`} product={product} highlightLabel={highlightLabel} />
        ))}
      </div>
    </section>
  );
}

export default function HomeCollections() {
  const featured = products.slice(0, 4);
  const newArrivals = [...products].sort((a, b) => b.aiScore - a.aiScore).slice(4, 8);
  const topAiPicks = [...products].sort((a, b) => b.aiScore - a.aiScore).slice(0, 4);

  return (
    <>
      <ProductRail
        title="Featured Products"
        subtitle="Handpicked products balancing performance, reliability, and value."
        items={featured}
        highlightLabel="Featured"
      />

      <ProductRail
        title="New Arrivals"
        subtitle="Fresh additions to the catalog curated for current buying trends."
        items={newArrivals}
        highlightLabel="New"
      />

      <ProductRail
        title="Top AI Picks"
        subtitle="Products with the strongest quality-to-value profile right now."
        items={topAiPicks}
        highlightLabel="AI Pick"
      />
    </>
  );
}
