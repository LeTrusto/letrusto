"use client";

import { useState } from "react";
import { Search, AlertTriangle, CheckCircle, XCircle, HelpCircle, Package } from "lucide-react";

type ValidationProduct = {
  product_id: string;
  supplier: string;
  supplier_sku: string;
  title: string;
  category: string;
  cost_usd: number | null;
  cost_inr: number | null;
  images: number;
  variants: number;
  inventory: number | null;
  total_inventory: number | null;
  cj_inventory: number | null;
  factory_inventory: number | null;
  inventory_verification: string | null;
  warehouse: string;
  weight_grams: number | null;
  missing_fields: string[];
  shipping_can_ship: boolean | null;
  shipping_validation: string | null;
  shipping_cheapest_usd: number | null;
  shipping_estimated_days: string | null;
  shipping_carrier: string | null;
  selling_price_inr: number | null;
  contribution_inr: number | null;
  contribution_pct: number | null;
  margin_status: string | null;
  unknown_costs: string[];
  score: number | null;
  verdict: string | null;
  score_notes: string[];
};

type ValidationSummary = {
  supplier: string;
  products_imported: number;
  products_passing: number;
  products_review: number;
  products_rejected: number;
  avg_supplier_cost_usd: number | null;
  avg_contribution_inr: number | null;
  missing_data_fields: Record<string, number>;
  shipping_validation_status: string;
  products: ValidationProduct[];
};

function verdictIcon(verdict: string | null) {
  switch (verdict) {
    case "PASS": return <CheckCircle size={16} className="text-green-600" />;
    case "REVIEW": return <AlertTriangle size={16} className="text-amber-500" />;
    case "REJECT": return <XCircle size={16} className="text-red-500" />;
    default: return <HelpCircle size={16} className="text-zinc-400" />;
  }
}

function marginBadge(status: string | null) {
  const colors: Record<string, string> = {
    PROFITABLE: "bg-green-100 text-green-800",
    MARGINAL: "bg-amber-100 text-amber-800",
    UNPROFITABLE: "bg-red-100 text-red-800",
    UNKNOWN: "bg-zinc-100 text-zinc-600",
  };
  return (
    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase ${colors[status ?? "UNKNOWN"] ?? colors.UNKNOWN}`}>
      {status ?? "UNKNOWN"}
    </span>
  );
}

export default function SupplierValidationView() {
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState<ValidationSummary | null>(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!keyword.trim()) return;

    setLoading(true);
    setError("");
    setData(null);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const token = typeof window !== "undefined" ? localStorage.getItem("lt_access_token") : null;

      const res = await fetch(
        `${apiBase}/api/v1/supplier-validation/search?keyword=${encodeURIComponent(keyword)}&destination=IN&page_size=20`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );

      if (!res.ok) {
        const body = await res.text();
        setError(`API error ${res.status}: ${body.slice(0, 200)}`);
        return;
      }

      setData(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-6 py-8">
      <div className="flex items-center gap-3 mb-6">
        <Package size={24} strokeWidth={1.5} />
        <div>
          <h1 className="text-xl font-bold">Supplier Validation</h1>
          <p className="text-xs text-[var(--text-muted)]">Development tool — Phase 2 product economics validation</p>
        </div>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2 mb-8 max-w-lg">
        <input
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Search supplier products (e.g. hair clip, earrings, bracelet)"
          className="lt-input flex-1"
        />
        <button type="submit" disabled={loading} className="lt-btn lt-btn-md lt-btn-primary">
          <Search size={16} />
          {loading ? "Searching..." : "Validate"}
        </button>
      </form>

      {error && (
        <div className="lt-card p-4 border-red-200 bg-red-50 text-red-700 text-sm mb-6">{error}</div>
      )}

      {data && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            <SummaryCard label="Imported" value={data.products_imported} />
            <SummaryCard label="Passing" value={data.products_passing} color="text-green-600" />
            <SummaryCard label="Review" value={data.products_review} color="text-amber-500" />
            <SummaryCard label="Rejected" value={data.products_rejected} color="text-red-500" />
            <SummaryCard label="Avg Cost (USD)" value={data.avg_supplier_cost_usd ? `$${data.avg_supplier_cost_usd.toFixed(2)}` : "—"} />
          </div>

          {/* Missing Fields */}
          {Object.keys(data.missing_data_fields).length > 0 && (
            <div className="lt-card p-4 mb-6">
              <h3 className="text-sm font-bold mb-2">Missing Data Fields</h3>
              <div className="flex flex-wrap gap-2">
                {Object.entries(data.missing_data_fields).map(([field, count]) => (
                  <span key={field} className="text-xs bg-amber-50 text-amber-700 px-2 py-1 rounded">
                    {field}: {count} products
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Shipping Status */}
          <div className="lt-card p-4 mb-6">
            <h3 className="text-sm font-bold mb-1">Shipping to India</h3>
            <span className="text-sm text-[var(--text-secondary)]">{data.shipping_validation_status}</span>
          </div>

          {/* Products Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] text-left text-xs text-[var(--text-muted)] uppercase">
                  <th className="py-3 pr-4">Score</th>
                  <th className="py-3 pr-4">Product</th>
                  <th className="py-3 pr-4">Category</th>
                  <th className="py-3 pr-4">Cost (USD)</th>
                  <th className="py-3 pr-4">Shipping (USD)</th>
                  <th className="py-3 pr-4">Selling (INR)</th>
                  <th className="py-3 pr-4">Contribution</th>
                  <th className="py-3 pr-4">Margin</th>
                  <th className="py-3 pr-4">CJ Inventory</th>
                  <th className="py-3 pr-4">Factory Inventory</th>
                  <th className="py-3 pr-4">Issues</th>
                </tr>
              </thead>
              <tbody>
                {data.products.map((p) => (
                  <tr key={p.product_id} className="border-b border-[var(--border)] hover:bg-[var(--surface-soft)]">
                    <td className="py-3 pr-4">
                      <div className="flex items-center gap-1.5">
                        {verdictIcon(p.verdict)}
                        <span className="font-mono font-bold text-sm">{p.score ?? "—"}</span>
                      </div>
                    </td>
                    <td className="py-3 pr-4 max-w-[200px]">
                      <p className="font-medium truncate">{p.title}</p>
                      <p className="text-[10px] text-[var(--text-muted)]">{p.supplier_sku}</p>
                    </td>
                    <td className="py-3 pr-4 text-[var(--text-secondary)]">{p.category || "—"}</td>
                    <td className="py-3 pr-4 font-mono">{p.cost_usd != null ? `$${p.cost_usd.toFixed(2)}` : "—"}</td>
                    <td className="py-3 pr-4 font-mono">{p.shipping_cheapest_usd != null ? `$${p.shipping_cheapest_usd.toFixed(2)}` : "—"}</td>
                    <td className="py-3 pr-4 font-mono">{p.selling_price_inr != null ? `₹${p.selling_price_inr}` : "—"}</td>
                    <td className="py-3 pr-4 font-mono">
                      {p.contribution_inr != null ? (
                        <span className={p.contribution_inr > 0 ? "text-green-600" : "text-red-500"}>
                          ₹{p.contribution_inr.toFixed(0)} ({p.contribution_pct?.toFixed(1)}%)
                        </span>
                      ) : "—"}
                    </td>
                    <td className="py-3 pr-4">{marginBadge(p.margin_status)}</td>
                    <td className="py-3 pr-4 font-mono">{p.cj_inventory ?? p.inventory ?? "—"}</td>
                    <td className="py-3 pr-4 font-mono">{p.factory_inventory ?? "—"}</td>
                    <td className="py-3 pr-4">
                      {p.score_notes.length > 0 && (
                        <details className="text-[10px] text-[var(--text-muted)]">
                          <summary className="cursor-pointer">{p.score_notes.length} notes</summary>
                          <ul className="mt-1 space-y-0.5">
                            {p.score_notes.map((n, i) => <li key={i}>• {n}</li>)}
                          </ul>
                        </details>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {!data && !loading && !error && (
        <div className="text-center py-20 text-[var(--text-muted)]">
          <p>Enter a search keyword to validate products from the configured supplier.</p>
          <p className="text-xs mt-1">Requires admin authentication and CJ_API_KEY to be configured.</p>
        </div>
      )}
    </div>
  );
}

function SummaryCard({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="lt-card p-4 text-center">
      <p className="text-xs text-[var(--text-muted)] uppercase">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color ?? ""}`}>{value}</p>
    </div>
  );
}
