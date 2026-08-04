"use client";

import { ExternalLink } from "lucide-react";
import type { Product } from "@/types/products";
import type { ProductBuyLink } from "@/types/products";
import { API_BASE_URL, IS_API_CONFIGURED } from "@/services/api";
import { getAmazonAffiliateUrl, getFlipkartAffiliateUrl, trackAffiliateClick } from "@/lib/affiliate";

type ProductBuyButtonsProps = {
  product: Pick<Product, "id" | "name" | "category" | "amazonAsin" | "amazonAffiliateUrl" | "flipkartAffiliateUrl">;
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

export default function ProductBuyButtons({ product, links }: ProductBuyButtonsProps) {
  const amazonAffiliateUrl = getAmazonAffiliateUrl(product);
  const flipkartAffiliateUrl = getFlipkartAffiliateUrl(product);
  const retailerLinks = links.filter((link) => link.label !== "Amazon");

  if (!amazonAffiliateUrl && retailerLinks.length === 0) {
    return (
      <p className="text-sm text-gray-400">No purchase links available yet.</p>
    );
  }

  return (
    <div className="space-y-3">
      {amazonAffiliateUrl ? (
        <a
          href={amazonAffiliateUrl}
          target="_blank"
          rel="noopener noreferrer sponsored"
          onClick={() => {
            trackAffiliateClick(product, "amazon");
          }}
          className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#232f3e] px-5 py-3.5 font-semibold text-white transition hover:bg-[#1b2530]"
        >
          Buy on Amazon
          <ExternalLink className="h-4 w-4 opacity-70" />
        </a>
      ) : (
        <button
          type="button"
          disabled
          className="inline-flex w-full cursor-not-allowed items-center justify-center gap-2 rounded-2xl border border-dashed border-gray-200 bg-gray-50 px-5 py-3.5 font-semibold text-gray-400"
        >
          Currently unavailable
        </button>
      )}

      {retailerLinks.map((link) => {
        const styleClass = RETAILER_STYLES[link.label] ?? RETAILER_STYLES.default;
        const href = link.label === "Flipkart" ? flipkartAffiliateUrl ?? link.href : link.href;
        const retailer = link.label.toLowerCase().replace(/\s+/g, "_");
        return (
          <a
            key={link.id || link.label}
            href={href}
            target="_blank"
            rel="noopener noreferrer sponsored"
            onClick={() => {
              void trackClick(link.id ?? 0);
              trackAffiliateClick(product, retailer);
            }}
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
