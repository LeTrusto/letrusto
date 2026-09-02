import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import DigitalProductPurchase from "@/components/digital-products/DigitalProductPurchase";
import ServiceCallout from "@/components/services/ServiceCallout";
import WorkbookPreview from "@/components/digital-products/WorkbookPreview";
import SchemaOrg from "@/components/SchemaOrg";
import { DIGITAL_PRODUCTS, formatDigitalProductPrice, getDigitalProductBySlug } from "@/lib/digitalProducts";

type ProductPageProps = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return DIGITAL_PRODUCTS.filter((product) => product.status === "published").map(({ slug }) => ({ slug }));
}

export async function generateMetadata({ params }: ProductPageProps): Promise<Metadata> {
  const product = getDigitalProductBySlug((await params).slug);
  return product ? { title: product.name, description: product.description, alternates: { canonical: `/digital-products/${product.slug}` } } : { title: "Digital Product" };
}

export default async function DigitalProductPage({ params }: ProductPageProps) {
  const product = getDigitalProductBySlug((await params).slug);
  if (!product) notFound();

  return (
    <main className="mx-auto max-w-7xl px-4 py-12 md:px-6 md:py-20">
      <SchemaOrg type="Product" data={{ name: product.name, description: product.description, category: product.category.name, brand: { "@type": "Brand", name: "LeTrusto" } }} />
      <Link href="/digital-products" className="text-sm font-semibold text-[var(--lt-primary)]">&larr; Digital Products</Link>
      <div className="mt-10 grid gap-12 lg:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)] lg:items-start">
        <div>
          <p className="lt-eyebrow">{product.category.name} / {product.format}</p>
          <h1 className="lt-heading-1 mt-3 max-w-3xl">{product.name}</h1>
          <p className="mt-5 max-w-2xl text-xl leading-relaxed text-[var(--text-secondary)]">{product.valueProposition}</p>
          <div className="mt-10"><WorkbookPreview product={product} /></div>
        </div>
        <DigitalProductPurchase product={product} />
      </div>
      <div className="mt-16 grid gap-12 border-t border-[var(--border)] pt-12 md:grid-cols-2">
        <section><h2 className="lt-heading-2">What you receive</h2><ul className="mt-5 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">{product.included.map((item) => <li key={item} className="border-b border-[var(--border)] pb-3">{item}</li>)}</ul></section>
        <section><h2 className="lt-heading-2">Who it is for</h2><ul className="mt-5 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">{product.audience.map((item) => <li key={item} className="border-b border-[var(--border)] pb-3">{item}</li>)}</ul><p className="mt-6 text-sm font-semibold text-[var(--text-primary)]">{formatDigitalProductPrice(product)} one-time purchase with protected download.</p></section>
      </div>
      <section className="mt-16 border-t border-[var(--border)] pt-12"><h2 className="lt-heading-2">How it helps</h2><ul className="mt-5 grid gap-3 text-sm leading-6 text-[var(--text-secondary)] md:grid-cols-2">{product.usage.map((item) => <li key={item} className="border-b border-[var(--border)] pb-3">{item}</li>)}</ul></section>
      <div className="mt-16"><ServiceCallout /></div>
    </main>
  );
}
