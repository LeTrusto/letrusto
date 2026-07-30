import Link from "next/link";

import type { ProductBuyLink } from "@/types/products";

type ProductBuyButtonsProps = {
  links: ProductBuyLink[];
};

const accentClasses: Record<ProductBuyLink["label"], string> = {
  Amazon: "bg-[#232f3e] text-white hover:bg-[#1b2530]",
  Flipkart: "bg-[#2874f0] text-white hover:bg-[#1f5dbf]",
  Croma: "bg-[#00a6d6] text-white hover:bg-[#0085ac]",
  "Reliance Digital": "bg-[#d91c5c] text-white hover:bg-[#b6164c]",
};

export default function ProductBuyButtons({ links }: ProductBuyButtonsProps) {
  return (
    <div className="space-y-3">
      {links.map((link) => (
        <Link
          key={link.label}
          href={link.href}
          target="_blank"
          rel="noreferrer"
          className={`inline-flex w-full items-center justify-center rounded-2xl px-5 py-3.5 font-semibold transition ${accentClasses[link.label]}`}
        >
          Buy on {link.label}
        </Link>
      ))}
    </div>
  );
}
