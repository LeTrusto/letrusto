import type { Metadata } from "next";

import Hero from "@/components/home/Hero";
import ProductRail from "@/components/home/ProductRail";
import ShopByStyle from "@/components/home/ShopByStyle";
import TrustSection from "@/components/home/TrustSection";
import NewsletterSignup from "@/components/home/NewsletterSignup";
import CreatorFinds from "@/components/home/CreatorFinds";
import SchemaOrg from "@/components/SchemaOrg";
import { getPublicProducts, toCommerceProduct } from "@/services/product.service";
import type { CommerceProduct } from "@/types/commerce";

export const metadata: Metadata = {
  title: "Trending Finds. Everyday Prices.",
  description: "Discover trending beauty, jewellery and style finds at everyday prices. LeTrusto — curated discovery commerce for India.",
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

export default async function Home() {
  let products: CommerceProduct[] = [];
  try {
    products = (await getPublicProducts()).map(toCommerceProduct);
  } catch {
    products = [];
  }

  return (
    <main className="bg-[#f8f7ea]">
      <SchemaOrg type="WebPage" data={{ name: "LeTrusto — Trending Finds. Everyday Prices.", url: "https://letrusto.com", description: "Discover trending beauty, jewellery and style finds at everyday prices." }} />
      <Hero />
      {products.length > 0 ? (
        <ProductRail title="Current catalog" subtitle="Products currently available from LeTrusto" products={products.slice(0, 8)} href="/shop" />
      ) : (
        <section className="mx-auto max-w-7xl px-4 py-14 text-center md:px-6">
          <h2 className="lt-heading-2">Our catalog is being prepared</h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">New LeTrusto products will appear here soon.</p>
        </section>
      )}
      <ShopByStyle />
      <CreatorFinds />
      <TrustSection />
      <NewsletterSignup />
    </main>
  );
}
