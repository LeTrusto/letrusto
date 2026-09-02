import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import DigitalProductPurchase from "@/components/digital-products/DigitalProductPurchase";
import DigitalProductViewTracker from "@/components/digital-products/DigitalProductViewTracker";
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
      <DigitalProductViewTracker product={product} />
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
      <section className="mt-16 grid gap-10 border-t border-[var(--border)] pt-12 md:grid-cols-2">
        <div>
          <p className="lt-eyebrow">A simple working loop</p>
          <h2 className="lt-heading-2 mt-2">Use the tools, then keep the habit</h2>
          <p className="lt-body mt-4">Use the free calculators for a quick decision, then use the toolkit to keep the inputs, scenarios and monthly review together.</p>
          <div className="mt-6 flex flex-wrap gap-3 text-sm font-semibold">
            <Link href="/tools/profit-margin-calculator" className="text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">Profit margin</Link>
            <Link href="/tools/pricing-calculator" className="text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">Pricing</Link>
            <Link href="/tools/break-even-calculator" className="text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">Break-even</Link>
            <Link href="/tools/expense-calculator" className="text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">Expenses</Link>
          </div>
        </div>
        <div className="border border-[var(--border)] bg-[var(--surface-soft)] p-6 md:p-8">
          <h2 className="lt-heading-2">What happens after purchase?</h2>
          <ol className="mt-5 space-y-4 text-sm leading-6 text-[var(--text-secondary)]">
            <li><strong className="text-[var(--text-primary)]">1. Verify payment.</strong> Razorpay payment details are checked by the backend before access is granted.</li>
            <li><strong className="text-[var(--text-primary)]">2. Open your account access.</strong> A verified purchase creates an entitlement on your LeTrusto account.</li>
            <li><strong className="text-[var(--text-primary)]">3. Download the file.</strong> Download the editable `.csv` spreadsheet from the protected product page.</li>
          </ol>
          <p className="mt-5 text-xs leading-5 text-[var(--text-muted)]">Need help with access or the file? Contact the <Link href="/support" className="font-semibold text-[var(--lt-primary)]">LeTrusto support team</Link>.</p>
        </div>
      </section>
      <div className="mt-16"><ServiceCallout /></div>
    </main>
  );
}
