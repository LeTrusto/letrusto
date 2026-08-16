"use client";

import { useState } from "react";
import { AlertTriangle, CheckCircle, ChevronRight, PackageSearch, Search, XCircle } from "lucide-react";
import { buildApiUrl, buildQueryString } from "@/services/api";

type Pricing = {
  selling_price_inr: string;
  landed_cost_inr: string;
  contribution_before_cac_inr: string;
  contribution_after_target_cac_inr: string;
  cac_target_supported: boolean;
};
type Variant = {
  supplier_variant_id: string;
  supplier_variant_sku: string;
  name: string;
  cost_usd: number | null;
  phase2_cost_inr: number | null;
  launch_cost_inr: string | null;
  weight_grams: number | null;
  total_inventory: number | null;
  cj_inventory: number | null;
  factory_inventory: number | null;
  pricing: Pricing | null;
};
type Recommendation = "APPROVED_CANDIDATE" | "REVIEW" | "REJECTED";
type DiscoveryProduct = {
  rank: number;
  recommendation: Recommendation;
  recommendation_reasons: string[];
  canonical_product_id: string;
  supplier_sku: string;
  title: string;
  category: string;
  images: string[];
  weight_grams: number | null;
  total_inventory: number | null;
  cj_inventory: number | null;
  factory_inventory: number | null;
  missing_fields: string[];
  variants: Variant[];
  shipping_based_on_variant_id: string | null;
  shipping_can_ship: boolean | null;
  shipping_validation: string | null;
  shipping_options: Array<{ carrier: string; method: string; cost_usd: number; cost_inr: string; estimated_days: string }>;
  phase2_score: number;
  phase2_verdict: string;
  phase2_score_notes: string[];
  commercial_review: { decision: string; reasons: string[]; cac_target_supported: boolean; target_margin_met_count: number; valid_variant_count: number };
  market_status: string;
  ranking_factors: { min_contribution_before_cac_inr: string | null; max_contribution_before_cac_inr: string | null; min_contribution_after_cac_inr: string | null; max_contribution_after_cac_inr: string | null; data_completeness_score: number };
};
type DiscoveryResponse = {
  elapsed_seconds: number;
  requested_count: number;
  returned_count: number;
  success_count: number;
  failed_count: number;
  verdict_counts: { approved_candidate: number; review: number; rejected: number };
  ranking_method: string[];
  top_recommendations: DiscoveryProduct[];
  products: DiscoveryProduct[];
  failures: Array<{ requested_product_id: string; title: string; stage: string; error: string }>;
};

const money = (value: string | number | null) => value == null ? "—" : `₹${Number(value).toFixed(2)}`;
const badgeStyle = (value: Recommendation) => value === "APPROVED_CANDIDATE" ? "bg-emerald-100 text-emerald-800" : value === "REJECTED" ? "bg-red-100 text-red-800" : "bg-amber-100 text-amber-800";

export default function SupplierValidationView() {
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState<DiscoveryResponse | null>(null);

  async function handleDiscovery(event: React.FormEvent) {
    event.preventDefault();
    const query = keyword.trim();
    if (!query || loading) return;
    setLoading(true);
    setError("");
    setData(null);
    try {
      const token = localStorage.getItem("lt_access_token");
      const url = buildApiUrl("/admin/supplier-discovery") + buildQueryString({ keyword: query, destination: "IN", page_size: 20 });
      const response = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
      if (!response.ok) {
        const body = await response.json().catch(() => null) as { detail?: string } | null;
        throw new Error(body?.detail ?? `Discovery failed (${response.status})`);
      }
      setData(await response.json() as DiscoveryResponse);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Discovery request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-[1500px] px-4 py-8 md:px-6">
      <header className="mb-6 flex items-center gap-3"><PackageSearch size={25} strokeWidth={1.6} /><div><h1 className="text-xl font-bold">Product Discovery & Selection</h1><p className="text-xs text-[var(--text-muted)]">Read-only CJ validation, launch economics, commercial screening, and ranking</p></div></header>
      <form onSubmit={handleDiscovery} className="mb-8 flex max-w-2xl gap-2">
        <input className="lt-input flex-1" disabled={loading} onChange={(event) => setKeyword(event.target.value)} placeholder="Search CJ products" type="search" value={keyword} />
        <button className="lt-btn lt-btn-md lt-btn-primary min-w-32" disabled={loading || !keyword.trim()} type="submit"><Search size={16} />{loading ? "Validating…" : "Validate"}</button>
      </form>
      {loading && <p className="mb-6 text-sm text-[var(--text-secondary)]">Processing up to 20 products. Detail, inventory, and freight checks can take several minutes.</p>}
      {error && <div className="mb-6 border border-red-200 bg-red-50 p-4 text-sm text-red-800">{error}</div>}
      {data && <div className="space-y-8">
        <section className="grid grid-cols-2 gap-3 md:grid-cols-4 lg:grid-cols-7" aria-label="Discovery summary">
          <Metric label="Elapsed" value={`${data.elapsed_seconds.toFixed(1)}s`} /><Metric label="Returned" value={`${data.returned_count}/${data.requested_count}`} /><Metric label="Processed" value={data.success_count} /><Metric label="Failed" value={data.failed_count} tone="text-red-600" /><Metric label="Candidates" value={data.verdict_counts.approved_candidate} tone="text-emerald-700" /><Metric label="Review" value={data.verdict_counts.review} tone="text-amber-700" /><Metric label="Rejected" value={data.verdict_counts.rejected} tone="text-red-700" />
        </section>
        <section>
          <div className="mb-3 flex items-end justify-between gap-4"><div><h2 className="text-base font-bold">Top recommendations</h2><p className="text-xs text-[var(--text-muted)]">Conservative worst-variant economics; market data is informational and unavailable during discovery.</p></div><details className="text-xs text-[var(--text-muted)]"><summary className="cursor-pointer">Ranking method</summary><ol className="mt-2 list-decimal space-y-1 pl-4">{data.ranking_method.map((item) => <li key={item}>{item}</li>)}</ol></details></div>
          <div className="grid gap-4 lg:grid-cols-3">{data.top_recommendations.map((product) => <article className="lt-card p-4" key={product.canonical_product_id}><div className="mb-3 flex items-start justify-between gap-3"><span className="font-mono text-2xl font-bold text-[var(--text-muted)]">#{product.rank}</span><RecommendationBadge value={product.recommendation} /></div><h3 className="line-clamp-2 text-sm font-bold">{product.title}</h3><p className="mt-1 truncate font-mono text-[10px] text-[var(--text-muted)]">{product.canonical_product_id}</p><dl className="mt-4 grid grid-cols-2 gap-3 text-xs"><Fact label="Phase 2 score" value={`${product.phase2_score} · ${product.phase2_verdict}`} /><Fact label="CJ inventory" value={product.cj_inventory ?? "Unknown"} /><Fact label="Worst pre-CAC" value={money(product.ranking_factors.min_contribution_before_cac_inr)} /><Fact label="Worst post-CAC" value={money(product.ranking_factors.min_contribution_after_cac_inr)} /></dl></article>)}</div>
        </section>
        {data.failures.length > 0 && <section className="border border-amber-200 bg-amber-50 p-4"><h2 className="mb-2 text-sm font-bold text-amber-900">Products requiring retry or manual review</h2><div className="space-y-2 text-xs text-amber-900">{data.failures.map((failure) => <p key={failure.requested_product_id}><b>{failure.title || failure.requested_product_id}</b> · {failure.stage} · {failure.error}</p>)}</div></section>}
        <section><h2 className="mb-3 text-base font-bold">Complete ranking</h2><div className="space-y-3">{data.products.map((product) => <RankedProduct key={product.canonical_product_id} product={product} />)}</div></section>
      </div>}
    </main>
  );
}

function RankedProduct({ product }: { product: DiscoveryProduct }) {
  const shipping = product.shipping_options[0];
  return <details className="lt-card group" open={product.rank <= 3}>
    <summary className="grid cursor-pointer list-none items-center gap-3 p-4 md:grid-cols-[44px_minmax(220px,2fr)_110px_130px_130px_150px_20px]">
      <span className="font-mono text-lg font-bold">#{product.rank}</span><div className="min-w-0"><div className="flex items-center gap-2"><RecommendationIcon value={product.recommendation} /><b className="truncate text-sm">{product.title}</b></div><p className="truncate font-mono text-[10px] text-[var(--text-muted)]">{product.canonical_product_id} · {product.supplier_sku}</p></div><Fact label="Phase 2" value={`${product.phase2_score} ${product.phase2_verdict}`} /><Fact label="Pre-CAC range" value={`${money(product.ranking_factors.min_contribution_before_cac_inr)}–${money(product.ranking_factors.max_contribution_before_cac_inr)}`} /><Fact label="Post-CAC range" value={`${money(product.ranking_factors.min_contribution_after_cac_inr)}–${money(product.ranking_factors.max_contribution_after_cac_inr)}`} /><RecommendationBadge value={product.recommendation} /><ChevronRight size={17} className="transition-transform group-open:rotate-90" />
    </summary>
    <div className="border-t border-[var(--border)] p-4">
      <div className="mb-5 grid gap-5 text-xs md:grid-cols-2 xl:grid-cols-4">
        <div><h4 className="mb-2 font-bold">Product & inventory</h4><p>{product.category || "Uncategorized"} · {product.weight_grams ?? "?"}g · {product.images.length} images</p><p>CJ sellable {product.cj_inventory ?? "unknown"} · Factory {product.factory_inventory ?? "unknown"} · Total {product.total_inventory ?? "unknown"}</p><p>Completeness {product.ranking_factors.data_completeness_score}/10 · Missing {product.missing_fields.join(", ") || "none"}</p></div>
        <div><h4 className="mb-2 font-bold">Shipping evidence</h4><p>{product.shipping_validation ?? "Unknown"} · {product.shipping_can_ship ? "Ships to IN" : "Not confirmed"}</p><p>{shipping ? `${shipping.carrier} ${shipping.method} · $${shipping.cost_usd.toFixed(2)} / ${money(shipping.cost_inr)} · ${shipping.estimated_days}` : "No shipping option"}</p><p className="mt-1 text-amber-700">Based on first variant {product.shipping_based_on_variant_id ?? "unknown"}; applied to all variant calculations.</p></div>
        <div><h4 className="mb-2 font-bold">Commercial screening</h4><p>{product.commercial_review.decision} · CAC {product.commercial_review.cac_target_supported ? "supported" : "not supported"}</p><p>{product.commercial_review.target_margin_met_count}/{product.commercial_review.valid_variant_count} variants meet target margin</p><p>{product.market_status}</p></div>
        <div><h4 className="mb-2 font-bold">Reasons</h4><p>{[...new Set([...product.recommendation_reasons, ...product.phase2_score_notes])].join(" · ") || "No review notes"}</p></div>
      </div>
      <div className="overflow-x-auto"><table className="w-full min-w-[1050px] text-left text-xs"><thead className="border-b border-[var(--border)] text-[var(--text-muted)]"><tr><th className="py-2">Variant</th><th>USD cost</th><th>Launch INR</th><th>Weight</th><th>CJ / Factory / Total</th><th>Landed</th><th>Selling</th><th>Pre-CAC</th><th>Post-CAC</th><th>CAC</th></tr></thead><tbody>{product.variants.map((variant) => <tr className="border-b border-[var(--border)]" key={variant.supplier_variant_id}><td className="py-2 pr-3"><b>{variant.name || "Variant"}</b><br /><span className="font-mono text-[10px] text-[var(--text-muted)]">{variant.supplier_variant_id}<br />{variant.supplier_variant_sku}</span></td><td>${variant.cost_usd?.toFixed(2) ?? "—"}</td><td>{money(variant.launch_cost_inr)}<br /><span className="text-[10px] text-[var(--text-muted)]">Phase 2 {money(variant.phase2_cost_inr)}</span></td><td>{variant.weight_grams ?? "—"}g</td><td>{variant.cj_inventory ?? "—"} / {variant.factory_inventory ?? "—"} / {variant.total_inventory ?? "—"}</td><td>{money(variant.pricing?.landed_cost_inr ?? null)}</td><td>{money(variant.pricing?.selling_price_inr ?? null)}</td><td>{money(variant.pricing?.contribution_before_cac_inr ?? null)}</td><td>{money(variant.pricing?.contribution_after_target_cac_inr ?? null)}</td><td>{variant.pricing?.cac_target_supported ? "Supported" : "Not supported"}</td></tr>)}</tbody></table></div>
    </div>
  </details>;
}

function RecommendationIcon({ value }: { value: Recommendation }) { if (value === "APPROVED_CANDIDATE") return <CheckCircle size={16} className="text-emerald-600" />; if (value === "REJECTED") return <XCircle size={16} className="text-red-600" />; return <AlertTriangle size={16} className="text-amber-600" />; }
function RecommendationBadge({ value }: { value: Recommendation }) { return <span className={`w-fit px-2 py-1 text-[10px] font-bold ${badgeStyle(value)}`}>{value.replace("_", " ")}</span>; }
function Metric({ label, value, tone = "" }: { label: string; value: string | number; tone?: string }) { return <div className="border-b-2 border-[var(--border)] px-2 py-3"><p className="text-[10px] uppercase text-[var(--text-muted)]">{label}</p><p className={`mt-1 text-xl font-bold ${tone}`}>{value}</p></div>; }
function Fact({ label, value }: { label: string; value: string | number }) { return <div><dt className="text-[10px] uppercase text-[var(--text-muted)]">{label}</dt><dd className="mt-0.5 font-medium">{value}</dd></div>; }