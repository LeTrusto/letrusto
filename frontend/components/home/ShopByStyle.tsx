import Link from "next/link";
import { type CommerceCategory, CATEGORY_MAP } from "@/types/commerce";
import { Gem, Scissors, Sparkles, ShoppingBag, Gift } from "lucide-react";

const CATEGORIES: { id: CommerceCategory; icon: typeof Gem }[] = [
  { id: "jewellery", icon: Gem },
  { id: "hair-style", icon: Scissors },
  { id: "beauty-tools", icon: Sparkles },
  { id: "accessories", icon: ShoppingBag },
  { id: "gifts", icon: Gift },
];

export default function ShopByStyle() {
  return (
    <section className="py-12 md:py-16">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        <h2 className="lt-heading-2 text-center">Shop by Style</h2>
        <p className="mt-2 text-center text-[var(--text-secondary)] text-sm">Find exactly what you&apos;re looking for</p>
        <div className="mt-8 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            return (
              <Link
                key={cat.id}
                href={`/shop?category=${cat.id}`}
                className="lt-card lt-card-hover flex flex-col items-center gap-3 py-6 text-center"
              >
                <div className="w-12 h-12 rounded-full bg-[var(--surface-muted)] flex items-center justify-center">
                  <Icon size={22} strokeWidth={1.5} className="text-[var(--text-secondary)]" />
                </div>
                <span className="text-sm font-semibold text-[var(--text-primary)]">
                  {CATEGORY_MAP[cat.id]}
                </span>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
