import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import SchemaOrg from "@/components/SchemaOrg";
import DigitalProductPurchase from "@/components/digital-products/DigitalProductPurchase";
import ServiceCallout from "@/components/services/ServiceCallout";
import WorkbookPreview from "@/components/digital-products/WorkbookPreview";
import { DIGITAL_PRODUCTS, getDigitalProductBySlug, formatDigitalProductPrice } from "@/lib/digitalProducts";

type ProductPageProps = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return DIGITAL_PRODUCTS.filter((product) => product.status === "published").map((product) => ({ slug: product.slug }));
}

export async function generateMetadata({ params }: ProductPageProps): Promise<Metadata> {
  const product = getDigitalProductBySlug((await params).slug);
  if (!product) return { title: "Digital Product" };
  return { title: product.name, description: product.description, alternates: { canonical: `/digital-products/${product.slug}` }, openGraph: { title: `${product.name} | LeTrusto`, description: product.description, url: `/digital-products/${product.slug}`, siteName: "LeTrusto", type: "website" } };
}

export default async function DigitalProductPage({ params }: ProductPageProps) {
  const product = getDigitalProductBySlug((await params).slug);
  if (!product) notFound();

  return <main className="mx-auto max-w-7xl px-4 py-12 md:px-6 md:py-20"><SchemaOrg type="Product" data={{ name: product.name, description: product.description, category: product.category.name, brand: { "@type": "Brand", name: "LeTrusto" } }} /><SchemaOrg type="BreadcrumbList" data={{ itemListElement: [{ "@type": "ListItem", position: 1, name: "Digital Products", item: "/digital-products" }, { "@type": "ListItem", position: 2, name: product.name, item: `/digital-products/${product.slug}` }] }} /><Link href="/digital-products" className="text-sm font-semibold text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">&larr; Digital Products</Link><div className="mt-10 grid gap-12 lg:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)] lg:items-start"><div><p className="lt-eyebrow">{product.category.name} / {product.format}</p><h1 className="lt-heading-1 mt-3 max-w-3xl">{product.name}</h1><p className="mt-5 max-w-2xl text-xl leading-relaxed text-[var(--text-secondary)]">{product.valueProposition}</p><div className="mt-10"><WorkbookPreview product={product} /></div></div><DigitalProductPurchase product={product} /></div><div className="mt-16 grid gap-12 border-t border-[var(--border)] pt-12 md:grid-cols-2"><section><h2 className="lt-heading-2">What you receive</h2><ul className="mt-5 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">{product.included.map((item) => <li key={item} className="border-b border-[var(--border)] pb-3">{item}</li>)}</ul></section><section><h2 className="lt-heading-2">Who it is for</h2><ul className="mt-5 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">{product.audience.map((item) => <li key={item} className="border-b border-[var(--border)] pb-3">{item}</li>)}</ul><p className="mt-6 text-sm font-semibold text-[var(--text-primary)]">{formatDigitalProductPrice(product)} planned launch price; checkout is not available yet.</p></section></div><section className="mt-16 grid gap-12 border-t border-[var(--border)] pt-12 md:grid-cols-2"><div><h2 className="lt-heading-2">How to use it</h2><ol className="mt-5 list-decimal space-y-3 pl-5 text-sm leading-6 text-[var(--text-secondary)]">{product.usage.map((item) => <li key={item}>{item}</li>)}</ol></div><div><h2 className="lt-heading-2">Questions</h2><div className="mt-5 space-y-5">{product.faq.map((item) => <div key={item.question}><h3 className="font-bold text-[var(--text-primary)]">{item.question}</h3><p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{item.answer}</p></div>)}</div></div></section><ServiceCallout /></main>;
}