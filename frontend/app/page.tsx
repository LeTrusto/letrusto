import type { Metadata } from "next";

import Hero from "@/components/home/Hero";
import ProductRail from "@/components/home/ProductRail";
import ShopByStyle from "@/components/home/ShopByStyle";
import TrustSection from "@/components/home/TrustSection";
import NewsletterSignup from "@/components/home/NewsletterSignup";
import CreatorFinds from "@/components/home/CreatorFinds";
import SchemaOrg from "@/components/SchemaOrg";
import {
  getTrendingProducts,
  getNewDrops,
  getLetrustoPicks,
  getProductsUnderPrice,
  getBundleProducts,
} from "@/lib/mockData";

export const metadata: Metadata = {
  title: "Trending Finds. Everyday Prices.",
  description:
    "Discover trending beauty, jewellery and style finds at everyday prices. LeTrusto — curated discovery commerce for India.",
  alternates: { canonical: "/" },
  openGraph: {
    title: "LeTrusto — Trending Finds. Everyday Prices.",
    description: "Discover trending beauty, jewellery and style finds at everyday prices.",
    url: "/",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
};

export default function Home() {
  const trending = getTrendingProducts();
  const newDrops = getNewDrops();
  const picks = getLetrustoPicks();
  const under299 = getProductsUnderPrice(299);
  const under499 = getProductsUnderPrice(499);
  const bundles = getBundleProducts();

  return (
    <main className="bg-[#f8f7ea]">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "LeTrusto — Trending Finds. Everyday Prices.",
          url: "https://letrusto.com",
          description: "Discover trending beauty, jewellery and style finds at everyday prices.",
        }}
      />

      <Hero />

      <ProductRail
        title="Trending Now"
        subtitle="What everyone&apos;s adding to cart"
        products={trending}
        href="/shop?sort=trending"
      />

      <ShopByStyle />

      {under299.length > 0 && (
        <ProductRail
          title="Under ₹299"
          subtitle="Style doesn't need a big budget"
          products={under299}
          href="/shop?maxPrice=299"
        />
      )}

      {under499.length > 0 && (
        <ProductRail
          title="Under ₹499"
          products={under499}
          href="/shop?maxPrice=499"
        />
      )}

      {bundles.length > 0 && (
        <ProductRail
          title="Bundle & Save"
          subtitle="Curated sets at better prices"
          products={bundles}
          href="/shop?tag=bundle"
        />
      )}

      {newDrops.length > 0 && (
        <ProductRail
          title="New Drops"
          subtitle="Just landed"
          products={newDrops}
          href="/shop?sort=newest"
        />
      )}

      {picks.length > 0 && (
        <section className="py-10 md:py-14">
          <div className="max-w-7xl mx-auto px-4 md:px-6">
            <h2 className="lt-heading-2">LeTrusto Picks</h2>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">We don&apos;t list everything. We pick the finds worth seeing.</p>
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
              {picks.map((product) => (
                <div key={product.id}>
                  <ProductRailCard product={product} />
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <CreatorFinds />
      <TrustSection />
      <NewsletterSignup />
    </main>
  );
}

// Inline import to avoid circular — uses the same card component
import CommerceProductCard from "@/components/products/CommerceProductCard";
function ProductRailCard({ product }: { product: import("@/types/commerce").CommerceProduct }) {
  return <CommerceProductCard product={product} />;
}
