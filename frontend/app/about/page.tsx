import type { Metadata } from "next";
import Link from "next/link";

import SchemaOrg from "@/components/SchemaOrg";

export const metadata: Metadata = {
  title: "About LeTrusto",
  description: "Discover LeTrusto's made-to-order designs, global delivery, and customer-first approach.",
  alternates: {
    canonical: "/about",
  },
  openGraph: {
    title: "About LeTrusto",
    description: "Discover LeTrusto's made-to-order designs, global delivery, and customer-first approach.",
    url: "/about",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "About LeTrusto",
    description: "Discover LeTrusto's made-to-order designs, global delivery, and customer-first approach.",
    images: ["/images/og-default.svg"],
  },
};

export default function AboutPage() {
  const faqItems = [
    {
      q: "What does LeTrusto sell?",
      a: "LeTrusto offers original designs on made-to-order apparel, wall art, accessories, home goods, and stationery.",
    },
    {
      q: "Why are products made to order?",
      a: "Making products after an order helps us avoid unnecessary stock and bring fresh designs to the store without overproducing.",
    },
    {
      q: "Where do you deliver?",
      a: "We ship to supported destinations worldwide. Production and delivery times depend on the product and delivery address and are shown during checkout.",
    },
    {
      q: "Can I return a made-to-order item?",
      a: "Made-to-order items are not returnable for change of mind, but we will review items that arrive damaged, defective, or incorrectly fulfilled.",
    },
    {
      q: "How do you handle order issues?",
      a: "Contact us with your order number as soon as possible. We review delivery, damage, and fulfillment issues with our production and shipping partners.",
    },
    {
      q: "How can I contact LeTrusto?",
      a: "Use the Contact page or Support centre for order, product, and account questions.",
    },
  ];

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(168,85,247,0.12),_transparent_24%),radial-gradient(circle_at_top_right,_rgba(251,113,133,0.1),_transparent_22%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)]">
      <SchemaOrg
        type="WebPage"
        data={{
          name: "About LeTrusto",
          url: "https://letrusto.com/about",
          description: "Discover LeTrusto's made-to-order designs, global delivery, and customer-first approach.",
        }}
      />
      <SchemaOrg
        type="FAQPage"
        data={{
          mainEntity: faqItems.map((item) => ({
            "@type": "Question",
            name: item.q,
            acceptedAnswer: {
              "@type": "Answer",
              text: item.a,
            },
          })),
        }}
      />
      <section className="mx-auto max-w-6xl px-6 py-14 md:py-18">
        <div className="max-w-4xl">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">About LeTrusto</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950 md:text-6xl">Original designs, made when you order</h1>
          <p className="mt-5 max-w-3xl text-base leading-relaxed text-slate-600 md:text-lg">
            LeTrusto is a global print-on-demand storefront for expressive designs made for everyday life. We make each order with care, then ship it to you.
          </p>
        </div>

        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {[
            { title: "Made to order", copy: "Your product is created after checkout, helping us keep collections fresh and reduce unnecessary inventory." },
            { title: "Designed to last", copy: "We choose practical products and clear product details so you can order with confidence." },
            { title: "Shipped worldwide", copy: "Our fulfillment network helps us produce and deliver orders to customers across supported destinations." },
          ].map((item) => (
            <article key={item.title} className="rounded-[1.75rem] border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-950">{item.title}</h2>
              <p className="mt-3 text-sm leading-relaxed text-slate-600">{item.copy}</p>
            </article>
          ))}
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-black tracking-tight text-slate-950">How your order works</h2>
            <div className="mt-6 space-y-5 text-sm leading-7 text-slate-600">
              <p><strong className="text-slate-950">1. Choose a design:</strong> Browse our current collections and select the product and variant you want.</p>
              <p><strong className="text-slate-950">2. We produce it:</strong> Your order is sent to production after payment is confirmed.</p>
              <p><strong className="text-slate-950">3. Quality check:</strong> The finished item is checked and prepared for dispatch.</p>
              <p><strong className="text-slate-950">4. Track delivery:</strong> We email tracking details when your order leaves production.</p>
            </div>
          </section>

          <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-black tracking-tight text-slate-950">What we care about</h2>
            <div className="mt-6 space-y-5 text-sm leading-7 text-slate-600">
              <p>We keep product details, pricing, and delivery expectations clear before you place an order.</p>
              <p>We create collections with a focus on useful products, expressive artwork, and reliable everyday appeal.</p>
              <p>When something goes wrong, we want to hear about it and work toward a fair resolution.</p>
              <p>We protect customer information and use payment and fulfillment partners that help us operate the store securely.</p>
            </div>
          </section>
        </div>

        <section className="mt-12 grid gap-6 lg:grid-cols-2">
          <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-black tracking-tight text-slate-950">Product quality</h2>
            <div className="mt-5 space-y-4 text-sm leading-7 text-slate-600">
              <p>Every order is produced after checkout through fulfillment partners selected for product range, production quality, and delivery coverage.</p>
              <p>Colors and placement can vary slightly from on-screen previews because products are printed on different materials and viewed on different displays.</p>
              <p>If an order does not arrive as expected, our support team will review the details and help with the next step.</p>
            </div>
          </article>
          <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-black tracking-tight text-slate-950">Why shop LeTrusto</h2>
            <ul className="mt-5 space-y-3 text-sm leading-7 text-slate-600">
              <li className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 rounded-full bg-rose-600" aria-hidden="true" />Fresh designs across useful everyday products.</li>
              <li className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 rounded-full bg-rose-600" aria-hidden="true" />Made to order instead of held as excess stock.</li>
              <li className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 rounded-full bg-rose-600" aria-hidden="true" />Clear production, shipping, and returns information.</li>
              <li className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 rounded-full bg-rose-600" aria-hidden="true" />Customer support when an order needs attention.</li>
            </ul>
          </article>
        </section>

        <section className="mt-12 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-black tracking-tight text-slate-950">Frequently Asked Questions</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {faqItems.map((item) => (
              <article key={item.q} className="rounded-[1.25rem] bg-slate-50 p-5">
                <h3 className="text-base font-bold text-slate-950">{item.q}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{item.a}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="mt-12 rounded-[2rem] border border-slate-200 bg-slate-950 p-8 text-white shadow-sm md:p-10">
          <h2 className="text-3xl font-black tracking-tight">Contact Information</h2>
          <p className="mt-4 max-w-3xl text-sm leading-relaxed text-white/80 md:text-base">
            For questions about products, orders, delivery, or account access, contact hello@letrusto.com or use the support centre.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/support" className="rounded-2xl bg-white px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-slate-100">Open support centre</Link>
            <Link href="/shop" className="rounded-2xl border border-white/20 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">Browse designs</Link>
          </div>
        </section>
      </section>
    </main>
  );
}
