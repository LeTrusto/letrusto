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
    <section className="bg-[var(--background)] py-16 md:py-20">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-black text-[var(--text-primary)] mb-2">Shop by Category</h2>
          <p className="text-[var(--text-secondary)] font-medium">Find unique printed products across all collections</p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            return (
              <Link
                key={cat.id}
                href={`/shop?category=${cat.id}`}
                className="lt-card lt-card-hover flex flex-col items-center justify-center gap-4 py-8 px-4 text-center min-h-[220px]"
              >
                <div className="w-16 h-16 rounded-full bg-[var(--lt-primary)]/15 flex items-center justify-center">
                  <Icon size={44} strokeWidth={1.5} className="text-[var(--lt-primary)]" />
                </div>
                <span className="text-base font-bold text-[var(--text-primary)]">
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
