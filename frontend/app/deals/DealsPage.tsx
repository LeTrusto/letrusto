"use client";

import { Loader2, Percent, Sparkles, Tag, TrendingUp, Zap } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

import { API_BASE_URL, IS_API_CONFIGURED } from "@/services/api";

type DealItem = {
  id: number;
  product_id: string;
  product_name: string;
  product_slug: string;
  product_image: string | null;
  current_price: number;
  currency: string;
  deal_type: string;
  label: string;
  discount_percent: number;
  coupon_code: string | null;
  cashback_amount: number | null;
  valid_until: string | null;
};

type DealsData = {
  today_deals: DealItem[];
  festival_offers: DealItem[];
  cashback_deals: DealItem[];
  coupon_deals: DealItem[];
  trending: DealItem[];
  ai_recommended: DealItem[];
};

function DealCard({ deal }: { deal: DealItem }) {
  return (
    <Link
      href={`/products/${deal.product_slug}`}
      className="group rounded-2xl border border-gray-100 bg-white p-4 shadow-sm transition hover:shadow-lg hover:-translate-y-0.5"
    >
      <div className="relative mb-3 aspect-square overflow-hidden rounded-xl bg-gray-50">
        {deal.product_image ? (
          <Image
            src={deal.product_image}
            alt={deal.product_name}
            fill
            className="object-contain p-2"
            sizes="200px"
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <Tag className="h-8 w-8 text-gray-300" />
          </div>
        )}
        {deal.discount_percent > 0 && (
          <span className="absolute right-2 top-2 rounded-full bg-green-500 px-2 py-0.5 text-xs font-bold text-white">
            {deal.discount_percent}% OFF
          </span>
        )}
        {deal.coupon_code && (
          <span className="absolute left-2 top-2 rounded-full bg-purple-600 px-2 py-0.5 text-xs font-bold text-white">
            COUPON
          </span>
        )}
      </div>
      <h3 className="mb-1 line-clamp-2 text-sm font-semibold text-slate-800 group-hover:text-purple-700">
        {deal.product_name}
      </h3>
      <div className="flex items-center justify-between">
        <span className="text-lg font-black text-slate-900">
          ₹{deal.current_price.toLocaleString()}
        </span>
        <span className="rounded-full bg-purple-100 px-2 py-0.5 text-xs font-semibold text-purple-700">
          {deal.label}
        </span>
      </div>
      {deal.coupon_code && (
        <div className="mt-2 rounded-lg bg-purple-50 px-3 py-1.5 text-xs font-bold text-purple-700">
          Code: {deal.coupon_code}
        </div>
      )}
      {deal.cashback_amount && (
        <div className="mt-2 rounded-lg bg-green-50 px-3 py-1.5 text-xs font-semibold text-green-700">
          Cashback: ₹{deal.cashback_amount.toLocaleString()}
        </div>
      )}
    </Link>
  );
}

function DealSection({
  title,
  icon: Icon,
  deals,
  iconClass,
}: {
  title: string;
  icon: React.ElementType;
  deals: DealItem[];
  iconClass?: string;
}) {
  if (deals.length === 0) return null;
  return (
    <section className="mb-10">
      <div className="mb-4 flex items-center gap-3">
        <Icon className={`h-6 w-6 ${iconClass ?? "text-purple-600"}`} />
        <h2 className="text-xl font-black text-slate-900">{title}</h2>
        <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-sm font-semibold text-gray-600">
          {deals.length}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {deals.map((deal, i) => (
          <DealCard key={deal.id > 0 ? deal.id : `${deal.product_id}-${i}`} deal={deal} />
        ))}
      </div>
    </section>
  );
}

export default function DealsPage() {
  const [data, setData] = useState<DealsData | null>(null);
  // Lazy init: if API not configured, start as "done" (not loading)
  const [fetchDone, setFetchDone] = useState(() => !IS_API_CONFIGURED);
  const [apiError, setApiError] = useState("");
  const configError = IS_API_CONFIGURED ? "" : "API not configured — deals require backend connection.";
  const error = apiError || configError;
  const loading = !fetchDone;

  useEffect(() => {
    if (!IS_API_CONFIGURED) return; // already done via lazy init
    fetch(`${API_BASE_URL}/api/v1/deals`)
      .then((r) => {
        if (!r.ok) throw new Error("Failed to load deals");
        return r.json() as Promise<DealsData>;
      })
      .then((d) => { setData(d); setFetchDone(true); })
      .catch((e: unknown) => { setApiError(e instanceof Error ? e.message : "Failed to load deals"); setFetchDone(true); });
  }, []);

  if (loading) {
    return (
      <main className="flex flex-1 items-center justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
      </main>
    );
  }

  const totalDeals = data
    ? data.today_deals.length +
      data.festival_offers.length +
      data.cashback_deals.length +
      data.coupon_deals.length +
      data.trending.length +
      data.ai_recommended.length
    : 0;

  return (
    <main className="mx-auto max-w-7xl px-5 py-10 sm:px-6">
      {/* Hero */}
      <div className="mb-10 rounded-3xl bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 px-8 py-10 text-white">
        <h1 className="mb-2 text-4xl font-black">Deals Centre</h1>
        <p className="text-lg font-medium opacity-90">
          {totalDeals > 0
            ? `${totalDeals} deals curated by AI — updated daily`
            : "Discover discounts, cashback, and AI-recommended offers"}
        </p>
      </div>

      {error && (
        <div className="mb-8 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          {error}
        </div>
      )}

      {data && totalDeals === 0 && (
        <div className="py-16 text-center text-gray-400">
          <Tag className="mx-auto mb-4 h-12 w-12 opacity-30" />
          <p className="text-lg">No deals available right now. Check back soon!</p>
        </div>
      )}

      {data && (
        <>
          <DealSection title="Today's Deals" icon={Zap} deals={data.today_deals} iconClass="text-orange-500" />
          <DealSection title="AI Recommended" icon={Sparkles} deals={data.ai_recommended} iconClass="text-purple-600" />
          <DealSection title="Trending Now" icon={TrendingUp} deals={data.trending} iconClass="text-blue-600" />
          <DealSection title="Festival Offers" icon={Percent} deals={data.festival_offers} iconClass="text-pink-600" />
          <DealSection title="Cashback Deals" icon={Tag} deals={data.cashback_deals} iconClass="text-green-600" />
          <DealSection title="Coupon Codes" icon={Tag} deals={data.coupon_deals} iconClass="text-indigo-600" />
        </>
      )}
    </main>
  );
}
