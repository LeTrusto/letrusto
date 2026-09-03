import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight, Check, Download, FileSpreadsheet, LockKeyhole, LifeBuoy } from "lucide-react";
import DigitalProductPurchase from "@/components/digital-products/DigitalProductPurchase";
import DigitalProductViewTracker from "@/components/digital-products/DigitalProductViewTracker";
import ServiceCallout from "@/components/services/ServiceCallout";
import WorkbookPreview from "@/components/digital-products/WorkbookPreview";
import SchemaOrg from "@/components/SchemaOrg";
import { DIGITAL_PRODUCTS, getDigitalProductBySlug } from "@/lib/digitalProducts";

type ProductPageProps = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return DIGITAL_PRODUCTS.filter((product) => product.status === "published").map(({ slug }) => ({ slug }));
}

export async function generateMetadata({ params }: ProductPageProps): Promise<Metadata> {
  const product = getDigitalProductBySlug((await params).slug);
  return product ? { title: product.name, description: product.description, alternates: { canonical: `/digital-products/${product.slug}` }, openGraph: { title: `${product.name} | LeTrusto`, description: product.description, url: `/digital-products/${product.slug}`, siteName: "LeTrusto", type: "website" } } : { title: "Digital Product" };
}

export default async function DigitalProductPage({ params }: ProductPageProps) {
  const product = getDigitalProductBySlug((await params).slug);
  if (!product) notFound();
  const toolLinks = product.slug === "freelancer-agency-client-work-workbook"
    ? [{ href: "/tools/freelancer-rate-calculator", label: "Freelancer rate" }, { href: "/tools/pricing-calculator", label: "Pricing" }, { href: "/tools/invoice-generator", label: "Invoice" }, { href: "/tools/commission-calculator", label: "Commission" }]
    : product.slug === "freelancer-rate-project-pricing-toolkit"
      ? [{ href: "/tools/freelancer-rate-calculator", label: "Freelancer rate" }, { href: "/tools/invoice-generator", label: "Invoice" }]
      : [{ href: "/tools/profit-margin-calculator", label: "Profit margin" }, { href: "/tools/pricing-calculator", label: "Pricing" }, { href: "/tools/break-even-calculator", label: "Break-even" }, { href: "/tools/expense-calculator", label: "Expenses" }];

  return (
    <main className="bg-[var(--background)] pb-24 lg:pb-0">
      <SchemaOrg type="Product" data={{ name: product.name, description: product.description, category: product.category.name, brand: { "@type": "Brand", name: "LeTrusto" }, offers: { "@type": "Offer", price: product.price, priceCurrency: product.currency, availability: "https://schema.org/InStock", url: `/digital-products/${product.slug}` } }} />
      <SchemaOrg type="FAQPage" data={{ mainEntity: product.faq.map((item) => ({ "@type": "Question", name: item.question, acceptedAnswer: { "@type": "Answer", text: item.answer } })) }} />
      <DigitalProductViewTracker product={product} />
      <section className="bg-[#26113c] text-white"><div className="mx-auto max-w-7xl px-4 py-8 md:px-6 md:py-12"><Link href="/digital-products" className="text-sm font-semibold text-purple-200 hover:text-white">&larr; All digital products</Link><div className="mt-10 grid gap-8 lg:grid-cols-[minmax(0,1.05fr)_minmax(280px,0.78fr)_minmax(280px,0.72fr)] lg:items-center"><div className="order-1"><p className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-pink-300"><FileSpreadsheet size={15} /> {product.category.name} / {product.format.split(",")[0]}</p><h1 className="mt-5 max-w-3xl text-4xl font-black leading-tight tracking-[-0.03em] md:text-6xl">{product.name}</h1><p className="mt-6 max-w-2xl text-lg leading-8 text-purple-100">{product.valueProposition}</p><div className="mt-7 flex flex-wrap gap-x-6 gap-y-3 text-sm text-purple-200"><span className="inline-flex items-center gap-2"><Check size={16} className="text-pink-300" />Editable workbook</span><span className="inline-flex items-center gap-2"><Download size={16} className="text-pink-300" />Protected digital delivery</span></div></div><div className="order-3 rounded-2xl border border-white/15 bg-white/10 p-3 shadow-2xl backdrop-blur-sm lg:order-2"><WorkbookPreview product={product} /></div><div className="order-2 lg:order-3"><DigitalProductPurchase product={product} /></div></div></div></section>
      <div className="mx-auto max-w-7xl px-4 py-10 md:px-6 md:py-16"><div className="grid gap-10"><div><div className="grid gap-3 sm:grid-cols-3"><Info icon={FileSpreadsheet} label="Format" value="Editable CSV" /><Info icon={Download} label="Delivery" value="Protected download" /><Info icon={LockKeyhole} label="Access" value="Your account" /></div><section className="mt-12"><p className="lt-eyebrow">Built for the problem in front of you</p><h2 className="lt-heading-2 mt-3">A clearer way to {product.slug.includes("finance") ? "run the numbers" : product.slug.includes("rate-project") ? "price your work" : "run client work"}.</h2><p className="lt-body mt-4 max-w-2xl">{product.description}</p></section><section className="mt-12 border-t border-[var(--border)] pt-10"><h2 className="lt-heading-2">What you receive</h2><ul className="mt-6 grid gap-3 sm:grid-cols-2">{product.included.map((item) => <li key={item} className="flex gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] p-4 text-sm leading-6 text-[var(--text-secondary)]"><Check size={17} className="mt-0.5 shrink-0 text-[var(--lt-accent)]" />{item}</li>)}</ul></section><section className="mt-12 border-t border-[var(--border)] pt-10"><h2 className="lt-heading-2">Who it is for</h2><div className="mt-5 flex flex-wrap gap-2">{product.audience.map((item) => <span key={item} className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm font-semibold text-[var(--text-secondary)]">{item}</span>)}</div></section></div></div>
      <section className="mt-16 grid gap-10 border-t border-[var(--border)] pt-12 md:grid-cols-2">
        <div>
          <p className="lt-eyebrow">A simple working loop</p>
          <h2 className="lt-heading-2 mt-2">Use the tools, then keep the habit</h2>
          <p className="lt-body mt-4">Use a free calculator for a quick decision, then keep the inputs, scenarios and review together in one editable workbook.</p>
          <div className="mt-6 flex flex-wrap gap-3 text-sm font-semibold">{toolLinks.map((tool) => <Link key={tool.href} href={tool.href} className="inline-flex items-center gap-1 text-[var(--lt-primary)] hover:text-[var(--lt-accent)]">{tool.label}<ArrowRight size={14} /></Link>)}</div>
        </div>
        <div className="border border-[var(--border)] bg-[var(--surface-soft)] p-6 md:p-8">
          <h2 className="lt-heading-2">What happens after purchase?</h2>
          <ol className="mt-5 space-y-4 text-sm leading-6 text-[var(--text-secondary)]">
            <li><strong className="text-[var(--text-primary)]">1. Verify payment.</strong> Razorpay payment details are checked by the backend before access is granted.</li>
            <li><strong className="text-[var(--text-primary)]">2. Open your account access.</strong> A verified purchase creates an entitlement on your LeTrusto account.</li>
            <li><strong className="text-[var(--text-primary)]">3. Download the file.</strong> Download the editable `.csv` spreadsheet from the protected product page.</li>
          </ol>
          <p className="mt-5 inline-flex items-start gap-2 text-xs leading-5 text-[var(--text-muted)]"><LifeBuoy size={15} className="mt-0.5 shrink-0" />Need help with access or the file? Contact the <Link href="/support" className="font-semibold text-[var(--lt-primary)]">LeTrusto support team</Link>.</p>
        </div>
      </section>
      <div className="mt-16"><ServiceCallout /></div></div>
    </main>
  );
}

function Info({ icon: Icon, label, value }: { icon: typeof FileSpreadsheet; label: string; value: string }) {
  return <div className="flex items-center gap-3 border border-[var(--border)] bg-[var(--surface)] p-4"><Icon size={19} className="shrink-0 text-[var(--lt-accent)]" /><div><p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[var(--text-muted)]">{label}</p><p className="mt-1 text-sm font-bold text-[var(--text-primary)]">{value}</p></div></div>;
}
