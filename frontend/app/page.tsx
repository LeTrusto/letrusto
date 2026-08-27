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
  title: "Unique Designs. Freshly Printed. Shipped Worldwide.",
  description: "Custom apparel, wall art and accessories — printed on demand and shipped worldwide. LeTrusto — unique designs, freshly printed.",
  alternates: { canonical: "/" },
  openGraph: {
    title: "LeTrusto — Unique Designs. Freshly Printed.",
    description: "Custom apparel, wall art and accessories — printed on demand and shipped worldwide.",
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
    <main className="bg-[var(--background)]">
      <SchemaOrg type="WebPage" data={{ name: "LeTrusto — Unique Designs. Freshly Printed.", url: "https://letrusto.com", description: "Custom apparel, wall art and accessories — printed on demand and shipped worldwide." }} />
      <Hero />
      {products.length > 0 ? (
        <ProductRail title="Fresh prints" subtitle="Custom designs printed on demand" products={products.slice(0, 8)} href="/shop" />
      ) : (
        <section className="mx-auto max-w-7xl px-4 py-14 text-center md:px-6">
          <h2 className="lt-heading-2">Our catalog is being prepared</h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">Unique printed products will appear here soon.</p>
        </section>
      )}
      <ShopByStyle />
      <CreatorFinds />
      <TrustSection />
      <NewsletterSignup />
    </main>
  );
}
