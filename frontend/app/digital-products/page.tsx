import type { Metadata } from "next";
import Link from "next/link";
import SchemaOrg from "@/components/SchemaOrg";
import DigitalProductCard from "@/components/digital-products/DigitalProductCard";
import { DIGITAL_PRODUCT_CATEGORIES, getPublishedDigitalProducts } from "@/lib/digitalProducts";

export const metadata: Metadata = {
  title: "Digital Products",
  description: "Ready-to-use business templates, spreadsheets, dashboards and practical digital resources from LeTrusto.",
  alternates: { canonical: "/digital-products" },
  openGraph: { title: "Digital Products | LeTrusto", description: "Ready-to-use business templates, spreadsheets, dashboards and practical digital resources from LeTrusto.", url: "/digital-products", siteName: "LeTrusto", type: "website" },
};

export default function DigitalProductsPage() {
  const products = getPublishedDigitalProducts();
  return (
    <main className="mx-auto max-w-7xl px-4 py-16 md:px-6 md:py-24">
      <SchemaOrg type="WebPage" data={{ name: "Digital Products", url: "/digital-products", description: metadata.description }} />
      <div className="max-w-3xl"><p className="lt-eyebrow">LeTrusto Digital Products</p><h1 className="lt-heading-1 mt-3">Useful systems for the work behind the work</h1><p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">Editable templates and practical resources for clearer decisions, calmer operations and better follow-through.</p></div>
      <section className="mt-14 border-y border-[var(--border)] py-8"><div className="grid gap-6 md:grid-cols-5">{DIGITAL_PRODUCT_CATEGORIES.map((category) => <Link key={category.slug} href={`#${category.slug}`} className="group"><p className="text-sm font-black text-[var(--text-primary)] group-hover:text-[var(--lt-primary)]">{category.name}</p><p className="mt-2 text-xs leading-5 text-[var(--text-secondary)]">{category.description}</p></Link>)}</div></section>
      <section id="business" className="mt-14"><div className="flex items-end justify-between gap-5"><div><p className="lt-eyebrow">Business</p><h2 className="lt-heading-2 mt-2">Built for practical decisions</h2></div><p className="text-sm text-[var(--text-muted)]">{products.length} product published</p></div><div className="mt-6 grid gap-6 lg:grid-cols-2">{products.map((product) => <DigitalProductCard key={product.id} product={product} />)}</div></section>
      <section className="mt-16 border-t border-[var(--border)] pt-10"><p className="text-sm font-bold text-[var(--text-primary)]">More categories are being developed carefully.</p><p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">Freelancer and agency, creator and marketing, career, and finance and productivity resources will appear here when they are useful enough to publish.</p></section>
    </main>
  );
}
