import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Check, Store, ShieldCheck } from "lucide-react";

export const metadata: Metadata = {
  title: "Social Proof Widgets for Shopify Stores",
  description: "Help Shopify store visitors see customer reviews, purchases, and stories with lightweight LeTrusto social proof widgets.",
  alternates: { canonical: "/social-proof-for-shopify" },
  openGraph: {
    title: "Social Proof Widgets for Shopify Stores | LeTrusto",
    description: "Make customer proof visible on your Shopify-style storefront with lightweight LeTrusto widgets.",
    url: "/social-proof-for-shopify",
    siteName: "LeTrusto",
    type: "website",
  },
};

const proofFormats = [
  "Recent purchase and signup activity",
  "Curated customer reviews and testimonials",
  "A lightweight widget that matches your storefront",
];

export default function ShopifySocialProofPage() {
  return (
    <main className="bg-[#f7faf8] text-[#17382e]">
      <section className="border-b border-[#d9e5df] bg-[#17382e] text-[#f7faf8]">
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
          <p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.24em] text-[#60a5fa]"><Store size={14} /> For growing online stores</p>
          <h1 className="mt-5 max-w-4xl text-4xl font-black tracking-tight sm:text-6xl">Show the proof your Shopify visitors need before they buy.</h1>
          <p className="mt-6 max-w-2xl text-base leading-7 text-[#c5d7cf] sm:text-lg">LeTrusto helps ecommerce teams collect, organize, and display customer proof through lightweight widgets that fit naturally into a storefront.</p>
          <div className="mt-8 flex flex-wrap gap-3"><Link href="/quiz" className="inline-flex items-center gap-2 bg-[#2563eb] px-5 py-3.5 text-sm font-bold text-white hover:bg-blue-500">Find your best widget <ArrowRight size={16} /></Link><Link href="/register" className="inline-flex items-center gap-2 border border-[#638378] px-5 py-3.5 text-sm font-bold text-white hover:border-[#60a5fa]">Start free <ArrowRight size={16} /></Link></div>
          <p className="mt-5 text-xs text-[#9bb4a8]">Works through a lightweight embed. No official Shopify App Store listing is implied.</p>
        </div>
      </section>
      <section className="mx-auto grid max-w-6xl gap-12 px-5 py-16 sm:px-8 lg:grid-cols-[0.9fr_1.1fr] lg:py-24">
        <div><p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#2563eb]">The trust gap</p><h2 className="mt-4 text-3xl font-black tracking-tight sm:text-4xl">Your customers may be convinced. New visitors are not there yet.</h2><p className="mt-5 text-base leading-7 text-[#587268]">A polished storefront still needs signals from people who have already chosen you. Put those experiences closer to the product, collection, or checkout decision.</p></div>
        <div className="border border-[#d9e5df] bg-white p-6 shadow-[0_18px_50px_rgba(23,56,46,0.07)] sm:p-8"><div className="flex items-center gap-3 border-b border-[#d9e5df] pb-5"><span className="flex h-10 w-10 items-center justify-center bg-[#2563eb] text-white"><ShieldCheck size={19} /></span><div><p className="text-sm font-black">LeTrusto proof layer</p><p className="text-xs text-[#71877f]">A calmer signal on your storefront</p></div></div><ul className="mt-6 space-y-4">{proofFormats.map((format) => <li key={format} className="flex items-start gap-3 text-sm leading-6 text-[#39564c]"><Check className="mt-1 h-4 w-4 shrink-0 text-[#0f766e]" />{format}</li>)}</ul><Link href="/dashboard/widgets" className="mt-8 inline-flex items-center gap-2 text-sm font-bold text-[#2563eb] hover:text-blue-700">Build your first widget <ArrowRight size={16} /></Link></div>
      </section>
      <section className="border-y border-[#d9e5df] bg-[#edf5f1] px-5 py-16 text-center sm:px-8 sm:py-20"><h2 className="text-3xl font-black tracking-tight sm:text-4xl">Turn customer experience into visible confidence.</h2><p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-[#587268]">Start with one widget, one real customer story, and one storefront page where trust matters.</p><Link href="/register" className="mt-7 inline-flex items-center gap-2 bg-[#17382e] px-5 py-3.5 text-sm font-bold text-white hover:bg-[#0f2b23]">Create your free account <ArrowRight size={16} /></Link></section>
    </main>
  );
}
