"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ChevronRight, Package } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { getAccountOrders } from "@/services/order.service";
import type { OrderList } from "@/types/orders";

function money(value: number) { return `₹${value.toLocaleString("en-IN")}`; }
function statusLabel(value: string) { return value.replaceAll("_", " "); }

export default function AccountOrdersPage() {
  const { accessToken, isLoading, isAuthenticated } = useAuth();
  const [data, setData] = useState<OrderList | null>(null);
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!accessToken) return;
    void getAccountOrders(accessToken, page)
      .then(setData)
      .catch(() => setError("Unable to load your orders."));
  }, [accessToken, page]);

  if (isLoading) return <main className="mx-auto max-w-3xl px-4 py-16 text-center">Loading orders...</main>;
  if (!isAuthenticated) return <main className="mx-auto max-w-3xl px-4 py-16 text-center"><h1 className="lt-heading-2">Sign in to view your orders</h1><Link href="/login?redirect=/account/orders" className="lt-btn lt-btn-primary mt-6 inline-flex">Sign In</Link></main>;

  return (
    <main className="mx-auto max-w-3xl px-4 py-8 md:py-12">
      <Link href="/account" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]">Account</Link>
      <h1 className="lt-heading-1 mt-3">My orders</h1>
      {error && <p role="alert" className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
      {!error && data && data.items.length === 0 && <div className="lt-card mt-8 py-14 text-center"><Package className="mx-auto text-[var(--text-muted)]" /><h2 className="mt-4 text-lg font-bold">No orders yet</h2><p className="mt-2 text-sm text-[var(--text-secondary)]">Your order history will appear here.</p><Link href="/shop" className="lt-btn lt-btn-primary mt-6 inline-flex">Shop now</Link></div>}
      <div className="mt-8 space-y-4">{data?.items.map((order) => <Link key={order.id} href={`/orders/${order.id}`} className="lt-card lt-card-hover block"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-bold">{order.order_number}</p><p className="mt-1 text-xs text-[var(--text-muted)]">{new Date(order.created_at).toLocaleDateString("en-IN")}</p></div><ChevronRight size={18} className="text-[var(--text-muted)]" /></div><div className="mt-5 grid grid-cols-2 gap-4 text-sm sm:grid-cols-4"><div><p className="lt-label">Total</p><p className="mt-1 font-bold">{money(order.total)}</p></div><div><p className="lt-label">Payment</p><p className="mt-1 font-semibold">{statusLabel(order.payment_status)}</p></div><div><p className="lt-label">Fulfillment</p><p className="mt-1 font-semibold">{statusLabel(order.fulfillment_status)}</p></div><div><p className="lt-label">Refund</p><p className="mt-1 font-semibold">{order.refund_status ? statusLabel(order.refund_status) : "—"}</p></div></div></Link>)}</div>
      {data && data.total > data.page_size && <div className="mt-8 flex items-center justify-between"><button disabled={page === 1} onClick={() => setPage((current) => current - 1)} className="lt-btn lt-btn-secondary">Previous</button><span className="text-sm text-[var(--text-secondary)]">Page {data.page}</span><button disabled={!data.has_next} onClick={() => setPage((current) => current + 1)} className="lt-btn lt-btn-secondary">Next</button></div>}
    </main>
  );
}
