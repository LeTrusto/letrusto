"use client";

import { ExternalLink } from "lucide-react";
import type { ProductBuyLink } from "@/types/products";
import { API_BASE_URL, IS_API_CONFIGURED } from "@/services/api";

type ProductBuyButtonsProps = {
  links: ProductBuyLink[];
};

const RETAILER_STYLES: Record<string, string> = {
  Amazon: "bg-[#232f3e] text-white hover:bg-[#1b2530]",
  Flipkart: "bg-[#2874f0] text-white hover:bg-[#1f5dbf]",
  Croma: "bg-[#00a6d6] text-white hover:bg-[#0085ac]",
  "Reliance Digital": "bg-[#d91c5c] text-white hover:bg-[#b6164c]",
  Hostinger: "bg-[#673de6] text-white hover:bg-[#5530cc]",
  Bluehost: "bg-[#2186e0] text-white hover:bg-[#1a6db0]",
  Namecheap: "bg-[#de3723] text-white hover:bg-[#b52d1c]",
  Semrush: "bg-[#ff6622] text-white hover:bg-[#e0551a]",
  Canva: "bg-[#00c4cc] text-white hover:bg-[#009ea5]",
  Grammarly: "bg-[#15c39a] text-white hover:bg-[#11a07e]",
  Notion: "bg-[#000000] text-white hover:bg-[#333333]",
  NordVPN: "bg-[#4687ff] text-white hover:bg-[#3570e0]",
  default: "bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:scale-[1.02]",
};

async function trackClick(linkId: number) {
  if (!IS_API_CONFIGURED || !linkId) return;
  try {
    await fetch(`${API_BASE_URL}/api/v1/affiliate/click/${linkId}`, { method: "POST" });
  } catch {
    // fire-and-forget — never block the user
  }
}

export default function ProductBuyButtons({ links }: ProductBuyButtonsProps) {
  if (!links || links.length === 0) {
    return (
      <p className="text-sm text-gray-400">No purchase links available yet.</p>
    );
  }

  return (
    <div className="space-y-3">
      {links.map((link) => {
        const styleClass = RETAILER_STYLES[link.label] ?? RETAILER_STYLES.default;
        return (
          <a
            key={link.id || link.label}
            href={link.href}
            target="_blank"
            rel="noreferrer noopener"
            onClick={() => { void trackClick(link.id ?? 0); }}
            className={`inline-flex w-full items-center justify-center gap-2 rounded-2xl px-5 py-3.5 font-semibold transition ${styleClass}`}
          >
            Buy on {link.label}
            <ExternalLink className="h-4 w-4 opacity-70" />
          </a>
        );
      })}
      <p className="text-center text-xs text-gray-400">
        Affiliate links — we may earn a commission at no extra cost to you.
      </p>
    </div>
  );
}
