import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Palette, ShoppingCart, Truck, Package } from "lucide-react";

export const metadata: Metadata = {
  title: "How It Works",
  description: "Learn how LeTrusto print-on-demand works for the current India launch.",
  alternates: { canonical: "/how-it-works" },
};

const STEPS = [
  {
    icon: Palette,
    title: "Browse Designs",
    description: "Explore our collection of unique, original designs across apparel, wall art, accessories and more.",
  },
  {
    icon: ShoppingCart,
    title: "Place Your Order",
    description: "Pick your product, size and colour. Pay securely with Razorpay.",
  },
  {
    icon: Package,
    title: "Printed Fresh",
    description: "Your product is printed on demand — no warehouse stock, just your chosen design made fresh for you.",
  },
  {
    icon: Truck,
    title: "India Checkout",
    description: "India is the current purchasing destination. Shipping is calculated at checkout before payment.",
  },
];

export default function HowItWorksPage() {
  return (
    <main className="bg-[var(--background)]">
      <section className="max-w-4xl mx-auto px-4 md:px-6 py-14 md:py-20">
        <h1 className="text-3xl md:text-5xl font-black tracking-tight text-[var(--text-primary)] text-center">
          How It Works
        </h1>
        <p className="mt-4 text-center text-[var(--text-secondary)] max-w-lg mx-auto">
          From design to made-to-order production, with India checkout available at launch.
        </p>

        <div className="mt-12 grid gap-8 md:grid-cols-2">
          {STEPS.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.title} className="lt-card p-6 flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[var(--surface-muted)] flex items-center justify-center">
                  <Icon size={22} strokeWidth={1.5} className="text-[var(--lt-purple)]" />
                </div>
                <div>
                  <p className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Step {index + 1}</p>
                  <h3 className="mt-1 text-lg font-bold text-[var(--text-primary)]">{step.title}</h3>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{step.description}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-12 text-center">
          <Link href="/shop" className="lt-btn lt-btn-lg lt-btn-primary">
            SHOP NOW
            <ArrowRight size={16} />
          </Link>
        </div>
      </section>
    </main>
  );
}
