"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ExternalLink, RefreshCw } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { API_BASE_URL } from "@/services/api";

type HistoryItem = {
  order_id: string;
  order_number: string;
  created_at: string;
  updated_at: string;
  customer_email: string;
  payment_status: string;
  payment_provider: string | null;
  provider_order_id: string | null;
  provider_reference: string | null;
  amount: number;
  currency: string;
  order_status: string;
  fulfillment_status: string;
  printful_order_id: string | null;
  printful_status: string | null;
  tracking_status: string;
  tracking_carrier: string | null;
  tracking_number: string | null;
  tracking_url: string | null;
  cancellation_status: string | null;
  refund_status: string | null;
  refund_amount: number | null;
  fulfillment_failure_category: string | null;
  fulfillment_failure: boolean;
  last_fulfillment_attempt_at: string | null;
  has_printful_order: boolean;
  timeline: { name: string; occurred_at: string }[];
};

type HistoryResponse = { items: HistoryItem[]; total: number; page: number; page_size: number };

const statusClass = (status: string) => status === "FAILED" ? "text-red-700" : status === "DELIVERED" ? "text-emerald-700" : "text-[var(--lt-primary)]";
const displayDate = (value: string | null) => value ? new Date(value).toLocaleString() : "Not recorded";

export default function FulfillmentHistoryPage() {
  const { accessToken, isLoading: authLoading, isAuthenticated, isAdmin } = useAuth();
  const [data, setData] = useState<HistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [orderNumber, setOrderNumber] = useState("");
  const [fulfillmentStatus, setFulfillmentStatus] = useState("");
  const [failedOnly, setFailedOnly] = useState(false);

  const loadHistory = useCallback(async (nextPage = page) => {
    if (!accessToken || !isAdmin) return;
    setLoading(true);
    setError("");
    const params = new URLSearchParams({ page: String(nextPage), page_size: "20" });
    if (orderNumber.trim()) params.set("order_number", orderNumber.trim());
    if (fulfillmentStatus) params.set("fulfillment_status", fulfillmentStatus);
    if (failedOnly) params.set("failed_fulfillment", "true");
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/fulfillment-history?${params}`, { headers: { Authorization: `Bearer ${accessToken}` } });
      if (!response.ok) throw new Error(response.status === 401 || response.status === 403 ? "Administrator access is required." : "Unable to load fulfillment history.");
      setData(await response.json() as HistoryResponse);
      setPage(nextPage);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load fulfillment history.");
    } finally {
      setLoading(false);
    }
  }, [accessToken, failedOnly, fulfillmentStatus, isAdmin, orderNumber, page]);

  useEffect(() => {
    if (accessToken && isAdmin) queueMicrotask(() => { void loadHistory(1); });
  }, [accessToken, isAdmin, loadHistory]);

  if (authLoading) return <main className="mx-auto max-w-7xl px-4 py-12"><p className="text-sm text-[var(--text-muted)]">Checking administrator access...</p></main>;
  if (!isAuthenticated || !isAdmin) return <main className="mx-auto max-w-3xl px-4 py-16 text-center"><h1 className="lt-heading-2">Administrator access required</h1><Link href="/login" className="lt-btn lt-btn-primary mt-6 inline-flex">Sign in</Link></main>;

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 md:px-6">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div><p className="text-xs font-semibold uppercase tracking-wide text-[var(--lt-primary)]">Operations</p><h1 className="mt-1 text-2xl font-bold">Fulfillment history</h1><p className="mt-1 text-sm text-[var(--text-muted)]">Printful order lifecycle, payment, delivery, and exception visibility.</p></div>
        <button type="button" onClick={() => void loadHistory()} className="lt-btn lt-btn-secondary inline-flex items-center gap-2"><RefreshCw size={16} aria-hidden="true" />Refresh</button>
      </div>
      <form onSubmit={(event) => { event.preventDefault(); void loadHistory(1); }} className="mb-6 grid gap-3 rounded-lg border border-[var(--border)] p-4 md:grid-cols-[1.5fr_1fr_auto_auto] md:items-end">
        <label className="text-sm">Order number<input value={orderNumber} onChange={(event) => setOrderNumber(event.target.value)} className="lt-input mt-1 w-full" placeholder="Search order number" /></label>
        <label className="text-sm">Fulfillment status<select value={fulfillmentStatus} onChange={(event) => setFulfillmentStatus(event.target.value)} className="lt-input mt-1 w-full"><option value="">All statuses</option><option value="PENDING">Pending</option><option value="SUBMITTED">Submitted</option><option value="PROCESSING">Processing</option><option value="SHIPPED">Shipped</option><option value="DELIVERED">Delivered</option><option value="FAILED">Failed</option></select></label>
        <label className="flex items-center gap-2 pb-2 text-sm"><input type="checkbox" checked={failedOnly} onChange={(event) => setFailedOnly(event.target.checked)} />Failed fulfillment</label>
        <button type="submit" className="lt-btn lt-btn-primary">Apply</button>
      </form>
      {error && <div role="alert" className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">{error}</div>}
      {loading ? <p className="py-12 text-center text-sm text-[var(--text-muted)]">Loading fulfillment history...</p> : data?.items.length === 0 ? <div className="rounded-lg border border-dashed border-[var(--border)] p-12 text-center"><h2 className="font-semibold">No fulfillment records</h2><p className="mt-1 text-sm text-[var(--text-muted)]">Paid Printful-backed orders matching these filters will appear here.</p></div> : <>
        <div className="hidden overflow-x-auto rounded-lg border border-[var(--border)] md:block"><table className="w-full text-left text-sm"><thead className="bg-[var(--surface-muted)] text-xs uppercase text-[var(--text-muted)]"><tr><th className="px-4 py-3">Order</th><th className="px-4 py-3">Payment</th><th className="px-4 py-3">Fulfillment</th><th className="px-4 py-3">Tracking</th><th className="px-4 py-3">Updated</th></tr></thead><tbody>{data?.items.map((item) => <tr key={item.order_id} className="border-t border-[var(--border)] align-top"><td className="px-4 py-4"><strong>{item.order_number}</strong><p className="mt-1 text-xs text-[var(--text-muted)]">{item.customer_email}</p><p className="mt-1 text-xs">{displayDate(item.created_at)}</p></td><td className="px-4 py-4"><strong>{item.payment_status}</strong><p className="mt-1 text-xs">{item.payment_provider || "Provider not recorded"}</p><p className="text-xs">{item.currency} {item.amount.toFixed(2)}</p></td><td className="px-4 py-4"><strong className={statusClass(item.fulfillment_status)}>{item.fulfillment_status}</strong><p className="mt-1 text-xs">{item.printful_order_id ? `Printful ${item.printful_order_id}` : "Printful order not created"}</p>{item.fulfillment_failure && <p className="mt-1 text-xs text-red-700">{item.fulfillment_failure_category}</p>}</td><td className="px-4 py-4"><strong>{item.tracking_status}</strong><p className="mt-1 text-xs">{item.tracking_carrier || "Carrier not recorded"}</p>{item.tracking_number && (item.tracking_url ? <a className="mt-1 inline-flex items-center gap-1 text-xs underline" href={item.tracking_url} target="_blank" rel="noreferrer">{item.tracking_number}<ExternalLink size={12} /></a> : <p className="mt-1 text-xs">{item.tracking_number}</p>)}</td><td className="px-4 py-4 text-xs">{displayDate(item.updated_at)}</td></tr>)}</tbody></table></div>
        <div className="grid gap-3 md:hidden">{data?.items.map((item) => <article key={item.order_id} className="rounded-lg border border-[var(--border)] p-4"><div className="flex items-start justify-between gap-3"><div><h2 className="font-semibold">{item.order_number}</h2><p className="text-xs text-[var(--text-muted)]">{item.customer_email}</p></div><span className={`text-xs font-semibold ${statusClass(item.fulfillment_status)}`}>{item.fulfillment_status}</span></div><dl className="mt-4 grid grid-cols-2 gap-3 text-xs"><div><dt className="text-[var(--text-muted)]">Payment</dt><dd>{item.payment_status} · {item.currency} {item.amount.toFixed(2)}</dd></div><div><dt className="text-[var(--text-muted)]">Printful</dt><dd>{item.printful_order_id || "Not created"}</dd></div><div><dt className="text-[var(--text-muted)]">Tracking</dt><dd>{item.tracking_number || item.tracking_status}</dd></div><div><dt className="text-[var(--text-muted)]">Updated</dt><dd>{displayDate(item.updated_at)}</dd></div></dl>{item.fulfillment_failure && <p className="mt-3 text-xs text-red-700">Failure: {item.fulfillment_failure_category}</p>}{item.tracking_url && <a className="mt-3 inline-flex items-center gap-1 text-sm underline" href={item.tracking_url} target="_blank" rel="noreferrer">Open tracking <ExternalLink size={14} /></a>}<details className="mt-4 border-t border-[var(--border)] pt-3"><summary className="cursor-pointer text-sm font-semibold">Timeline</summary><ol className="mt-3 space-y-2 text-xs">{item.timeline.map((event) => <li key={`${event.name}-${event.occurred_at}`}><strong>{event.name}</strong><span className="ml-2 text-[var(--text-muted)]">{displayDate(event.occurred_at)}</span></li>)}</ol></details></article>)}</div>
        <div className="mt-6 flex items-center justify-between text-sm"><span>{data?.total ?? 0} records</span><div className="flex gap-2"><button type="button" disabled={page <= 1 || loading} onClick={() => void loadHistory(page - 1)} className="lt-btn lt-btn-secondary">Previous</button><button type="button" disabled={!data || page * data.page_size >= data.total || loading} onClick={() => void loadHistory(page + 1)} className="lt-btn lt-btn-secondary">Next</button></div></div>
      </>}
    </main>
  );
}
