"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Download, Lock, RefreshCw } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { API_BASE_URL } from "@/services/api";

type Metric = { value: number | null; status: string; reason?: string | null };
type Summary = {
  period: { label: string };
  gross_order_value: number;
  paid_sales: number;
  refunded_amount: number;
  net_sales: number;
  payment_fees: Metric;
  landed_cost: Metric;
  shipping_cost: Metric;
  contribution_before_cac: Metric;
  cac: Metric;
  contribution_after_cac: Metric;
  marketing_spend: number;
  attributed_orders: number;
  attributed_sales: number;
  attributed_cac: Metric;
  blended_cac: Metric;
  roas: Metric;
  contribution_after_cac_status: string;
  policy_assumptions: { target_cac_inr: number };
  order_count: number;
  paid_order_count: number;
  pending_payment_count: number;
  status_breakdown: Record<string, number>;
};
type Product = { product_name: string; orders: number; units_sold: number; refunds: number; net_sales: number; contribution_before_cac: Metric; actual_cac: Metric; contribution_after_cac: Metric; cac_status: string };
type Inventory = { product_name: string; variant_name: string; cj_inventory: number | null; factory_inventory: number | null; active_reservations: number; available_customer_inventory: number; sellable_inventory_status: string };
type Trend = { date: string; orders: number; paid_orders: number; gross_sales: number; refunds: number; net_sales: number; marketing_spend: number; attributed_orders: number; actual_cac: number | null; contribution_after_cac: number | null; cac_status: string };

function money(value: number | null) { return value == null ? "—" : `₹${value.toLocaleString("en-IN")}`; }
function actual(metric: Metric) { if (metric.value != null) return money(metric.value); return metric.status === "NOT_ATTRIBUTED" ? "Not attributed" : metric.status === "NOT_CONFIGURED" ? "Not configured" : "Insufficient data"; }

export default function AdminAnalyticsView() {
  const { accessToken, isLoading, isAuthenticated, isAdmin } = useAuth();
  const [period, setPeriod] = useState("last_30_days");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [inventory, setInventory] = useState<Inventory[]>([]);
  const [trend, setTrend] = useState<Trend[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!accessToken || !isAdmin) return;
    void Promise.resolve().then(async () => {
      try {
        const headers = { Authorization: `Bearer ${accessToken}` };
        const query = `?period=${period}`;
        const responses = await Promise.all([
          fetch(`${API_BASE_URL}/api/v1/admin/analytics/summary${query}`, { headers }),
          fetch(`${API_BASE_URL}/api/v1/admin/analytics/products${query}`, { headers }),
          fetch(`${API_BASE_URL}/api/v1/admin/analytics/inventory`, { headers }),
          fetch(`${API_BASE_URL}/api/v1/admin/analytics/sales-trend${query}`, { headers }),
        ]);
        if (responses.some((response) => !response.ok)) throw new Error("Analytics request failed");
        setSummary((await responses[0].json()) as Summary);
        setProducts((await responses[1].json()) as Product[]);
        setInventory((await responses[2].json()) as Inventory[]);
        setTrend((await responses[3].json()) as Trend[]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load analytics");
      }
    });
  }, [accessToken, isAdmin, period]);

  async function downloadExport() {
    if (!accessToken) return;
    const response = await fetch(`${API_BASE_URL}/api/v1/admin/analytics/export?period=${period}`, { headers: { Authorization: `Bearer ${accessToken}` } });
    if (!response.ok) return;
    const url = URL.createObjectURL(await response.blob());
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "letrusto-analytics.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  if (isLoading) return <main className="mx-auto max-w-7xl px-5 py-16 text-center">Loading analytics...</main>;
  if (!isAuthenticated || !isAdmin) return <main className="mx-auto max-w-3xl px-5 py-16 text-center"><Lock className="mx-auto text-[var(--text-muted)]" /><h1 className="lt-heading-2 mt-4">Admin access required</h1><Link href="/login" className="lt-btn lt-btn-primary mt-6 inline-flex">Sign In</Link></main>;

  return (
    <main className="mx-auto max-w-7xl px-5 py-8 md:py-12">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="lt-label">Business operations</p><h1 className="lt-heading-1 mt-2">Analytics</h1><p className="mt-2 text-sm text-[var(--text-secondary)]">Actuals use stored order, payment, and refund dates. Unknown costs remain unavailable.</p></div>
        <div className="flex gap-2"><select aria-label="Reporting period" value={period} onChange={(event) => setPeriod(event.target.value)} className="lt-select"><option value="today">Today</option><option value="yesterday">Yesterday</option><option value="last_7_days">Last 7 days</option><option value="last_30_days">Last 30 days</option><option value="this_month">This month</option><option value="previous_month">Previous month</option></select><button type="button" onClick={() => void downloadExport()} className="lt-btn lt-btn-secondary"><Download size={15} /> Export</button></div>
      </header>
      {error && <p role="alert" className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
      {!summary && !error && <div className="lt-card mt-8 flex items-center gap-3 py-12 text-sm text-[var(--text-secondary)]"><RefreshCw size={16} className="animate-spin" /> Loading analytics...</div>}
      {summary && <>
        <section className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4"><Kpi label="Gross order value" value={money(summary.gross_order_value)} /><Kpi label="Paid sales" value={money(summary.paid_sales)} /><Kpi label="Refunded" value={money(summary.refunded_amount)} /><Kpi label="Net sales" value={money(summary.net_sales)} /></section>
        <section className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4"><Kpi label="Orders" value={String(summary.order_count)} /><Kpi label="Paid orders" value={String(summary.paid_order_count)} /><Kpi label="Pending payment" value={String(summary.pending_payment_count)} /><Kpi label="Average paid order" value={summary.paid_order_count ? money(summary.paid_sales / summary.paid_order_count) : "Not available"} /></section>
        <section className="mt-8 grid gap-4 md:grid-cols-4"><MetricCard label="Payment fees" metric={summary.payment_fees} /><MetricCard label="Landed cost" metric={summary.landed_cost} /><MetricCard label="Shipping cost" metric={summary.shipping_cost} /><MetricCard label="Contribution Before CAC" metric={summary.contribution_before_cac} /></section>
        <section className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4"><Kpi label="Marketing Spend" value={money(summary.marketing_spend)} /><MetricCard label="ACTUAL CAC" metric={summary.attributed_cac} /><MetricCard label="BLENDED CAC" metric={summary.blended_cac} /><Kpi label="TARGET CAC" value={money(summary.policy_assumptions.target_cac_inr)} /></section>
        <section className="mt-4 grid gap-4 md:grid-cols-3"><MetricCard label="Contribution After CAC" metric={summary.contribution_after_cac} /><MetricCard label="ROAS" metric={{ ...summary.roas, value: summary.roas.value == null ? null : summary.roas.value }} suffix="x" /><Kpi label="Attributed Orders" value={String(summary.attributed_orders)} /></section>
        <div className="mt-8 grid gap-8 lg:grid-cols-[1.3fr_1fr]">
          <section className="lt-card"><h2 className="text-lg font-bold">Sales trend</h2><div className="mt-4 overflow-x-auto"><table className="w-full text-left text-sm"><thead className="text-xs uppercase text-[var(--text-muted)]"><tr><th className="py-2 pr-4">Date</th><th className="py-2 pr-4">Net sales</th><th className="py-2 pr-4">Spend</th><th className="py-2 pr-4">Actual CAC</th><th className="py-2">After CAC</th></tr></thead><tbody>{trend.filter((point) => point.orders || point.paid_orders || point.refunds || point.marketing_spend).map((point) => <tr key={point.date} className="border-t border-[var(--border)]"><td className="py-2 pr-4">{point.date}</td><td className="py-2 pr-4">{money(point.net_sales)}</td><td className="py-2 pr-4">{money(point.marketing_spend)}</td><td className="py-2 pr-4">{point.actual_cac == null ? "Not attributed" : money(point.actual_cac)}</td><td className="py-2">{point.contribution_after_cac == null ? "—" : money(point.contribution_after_cac)}</td></tr>)}</tbody></table>{!trend.some((point) => point.orders || point.paid_orders || point.refunds || point.marketing_spend) && <Empty />}</div></section>
          <section className="lt-card"><h2 className="text-lg font-bold">Payment / fulfillment status</h2><div className="mt-4 space-y-2 text-sm">{Object.entries(summary.status_breakdown).map(([key, count]) => <div key={key} className="flex justify-between border-b border-[var(--border)] pb-2"><span>{key.replaceAll("_", " ")}</span><strong>{count}</strong></div>)}</div></section>
        </div>
        <div className="mt-8 grid gap-8 lg:grid-cols-[1.3fr_1fr]">
          <section className="lt-card"><h2 className="text-lg font-bold">Product performance</h2>{products.length === 0 ? <Empty /> : <div className="mt-4 overflow-x-auto"><table className="w-full text-left text-sm"><thead className="text-xs uppercase text-[var(--text-muted)]"><tr><th className="py-2 pr-4">Product</th><th className="py-2 pr-4">Net sales</th><th className="py-2 pr-4">Before CAC</th><th className="py-2 pr-4">Actual CAC</th><th className="py-2 pr-4">After CAC</th><th className="py-2">CAC status</th></tr></thead><tbody>{products.map((product) => <tr key={product.product_name} className="border-t border-[var(--border)]"><td className="py-3 pr-4 font-semibold">{product.product_name}</td><td className="py-3 pr-4">{money(product.net_sales)}</td><td className="py-3 pr-4">{actual(product.contribution_before_cac)}</td><td className="py-3 pr-4">{actual(product.actual_cac)}</td><td className="py-3 pr-4">{actual(product.contribution_after_cac)}</td><td className="py-3">{product.cac_status === "NOT_ATTRIBUTED" ? "Not attributed" : product.cac_status}</td></tr>)}</tbody></table></div>}</section>
          <section className="lt-card"><h2 className="text-lg font-bold">Inventory exposure</h2>{inventory.length === 0 ? <Empty /> : <div className="mt-4 space-y-3">{inventory.map((row) => <div key={`${row.product_name}-${row.variant_name}`} className="border-t border-[var(--border)] pt-3 first:border-0 first:pt-0"><p className="text-sm font-semibold">{row.product_name}</p><p className="text-xs text-[var(--text-secondary)]">{row.variant_name} · CJ {row.cj_inventory ?? "Unknown"} · Factory {row.factory_inventory ?? "Unknown"} · Reserved {row.active_reservations} · Available {row.available_customer_inventory}</p></div>)}</div>}</section>
        </div>
      </>}
    </main>
  );
}

function Kpi({ label, value }: { label: string; value: string }) { return <div className="lt-card"><p className="lt-label">{label}</p><p className="mt-2 text-xl font-bold">{value}</p></div>; }
function MetricCard({ label, metric, suffix = "" }: { label: string; metric: Metric; suffix?: string }) { return <div className="lt-card"><p className="lt-label">{label}</p><p className="mt-2 font-bold">{metric.value == null ? actual(metric) : `${actual(metric)}${suffix}`}</p><p className="mt-1 text-xs text-[var(--text-muted)]">{metric.value == null ? metric.reason : "Actual"}</p></div>; }
function Empty() { return <p className="mt-6 text-sm text-[var(--text-muted)]">No data for this period.</p>; }
