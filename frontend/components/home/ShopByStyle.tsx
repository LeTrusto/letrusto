import Link from "next/link";
import { type CommerceCategory, CATEGORY_MAP } from "@/types/commerce";
import { Shirt, Frame, ShoppingBag, Home, BookOpen } from "lucide-react";

const CATEGORIES: { id: CommerceCategory; icon: typeof Shirt }[] = [
  { id: "apparel", icon: Shirt },
  { id: "wall-art", icon: Frame },
  { id: "accessories", icon: ShoppingBag },
  { id: "home-living", icon: Home },
  { id: "stationery", icon: BookOpen },
];

export default function ShopByStyle() {
  return (
    <section className="py-12 md:py-16">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        <h2 className="lt-heading-2 text-center">Shop by Category</h2>
        <p className="mt-2 text-center text-[var(--text-secondary)] text-sm">Custom printed products shipped worldwide</p>
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
