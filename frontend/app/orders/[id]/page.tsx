"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ChevronLeft, Package, RotateCcw } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { cancelOrder, getOrder, verifyPendingOrderPayment } from "@/services/order.service";
import type { Order } from "@/types/orders";

function money(value: number) { return `₹${value.toLocaleString("en-IN")}`; }
function label(value: string) { return value.replaceAll("_", " "); }
function canCancel(order: Order) { return !order.cancelled_at && !order.refund_status && !order.tracking_number && !["PROCESSING", "SHIPPED", "DELIVERED"].includes(order.fulfillment_status); }

export default function OrderDetailPage() {
  const { accessToken, isLoading, isAuthenticated } = useAuth();
  const params = useParams<{ id: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState("");
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (!accessToken || !params.id) return;
    void Promise.resolve().then(async () => {
      try {
        const initial = await getOrder(accessToken, params.id);
        try { await verifyPendingOrderPayment(accessToken, initial); } catch { /* Pending payment is safe. */ }
        setOrder(await getOrder(accessToken, params.id));
      } catch (err) { setError(err instanceof Error ? err.message : "Unable to load order"); }
    });
  }, [accessToken, params.id]);

  async function handleCancel() {
    if (!accessToken || !order || !window.confirm("Cancel this order?")) return;
    setCancelling(true);
    setError("");
    try { await cancelOrder(accessToken, order.id); setOrder(await getOrder(accessToken, order.id)); } catch (err) { setError(err instanceof Error ? err.message : "Unable to cancel order"); } finally { setCancelling(false); }
  }

  if (isLoading) return <main className="mx-auto max-w-3xl px-4 py-16 text-center">Loading order...</main>;
  if (!isAuthenticated) return <main className="mx-auto max-w-3xl px-4 py-16 text-center"><h1 className="lt-heading-2">Sign in to view this order</h1><Link href={`/login?redirect=/orders/${params.id}`} className="lt-btn lt-btn-primary mt-6 inline-flex">Sign In</Link></main>;
  if (error && !order) return <main className="mx-auto max-w-3xl px-4 py-16 text-center"><p role="alert">{error}</p><Link href="/account/orders" className="lt-btn lt-btn-primary mt-6 inline-flex">Back to orders</Link></main>;
  if (!order) return <main className="mx-auto max-w-3xl px-4 py-16 text-center">Loading order...</main>;

  const cancellationBlocked = ["PROCESSING", "SHIPPED", "DELIVERED"].includes(order.fulfillment_status) || Boolean(order.tracking_number);
  const fulfillmentMessage = order.fulfillment_status === "SHIPPED" ? "Your order has shipped." : order.fulfillment_status === "DELIVERED" ? "Delivered" : order.fulfillment_status === "PROCESSING" ? "Your order is being prepared." : "Awaiting fulfillment.";

  return <main className="mx-auto max-w-3xl px-4 py-8 md:py-12"><Link href="/account/orders" className="inline-flex items-center gap-1 text-sm text-[var(--text-secondary)]"><ChevronLeft size={15} /> My orders</Link><div className="mt-5 flex items-start justify-between gap-4"><div><p className="lt-label">Order detail</p><h1 className="lt-heading-2 mt-2">{order.order_number}</h1><p className="mt-1 text-sm text-[var(--text-muted)]">{new Date(order.created_at).toLocaleDateString("en-IN", { dateStyle: "long" })}</p></div><Package className="text-[var(--lt-accent-dark)]" /></div>{error && <p role="alert" className="mt-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}<div className="lt-card mt-6 grid grid-cols-2 gap-4 text-sm sm:grid-cols-4"><div><p className="lt-label">Payment</p><p className="mt-1 font-bold">{label(order.payment_status)}</p></div><div><p className="lt-label">Fulfillment</p><p className="mt-1 font-bold">{label(order.fulfillment_status)}</p></div><div><p className="lt-label">Total</p><p className="mt-1 font-bold">{money(order.total)}</p></div><div><p className="lt-label">Refund</p><p className="mt-1 font-bold">{order.refund_status ? label(order.refund_status) : "—"}</p></div></div><section className="lt-card mt-4"><h2 className="text-lg font-bold">Items</h2><div className="mt-4 divide-y divide-[var(--border)]">{order.items.map((item) => <div key={item.id} className="flex gap-3 py-4 first:pt-0 last:pb-0"><div className="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-[var(--surface-muted)]">{item.product_image_url ? <div role="img" aria-label={`${item.product_name} image`} style={{ backgroundImage: `url(${item.product_image_url})` }} className="h-full w-full bg-cover bg-center" /> : <Package size={20} className="text-[var(--text-muted)]" />}</div><div className="min-w-0 flex-1"><p className="text-sm font-semibold">{item.product_name}</p><p className="mt-1 text-xs text-[var(--text-secondary)]">{item.variant_name} · Qty {item.quantity}</p></div><p className="text-sm font-bold">{money(item.line_total)}</p></div>)}</div><div className="mt-5 space-y-2 border-t border-[var(--border)] pt-4 text-sm"><div className="flex justify-between"><span>Subtotal</span><span>{money(order.subtotal)}</span></div><div className="flex justify-between"><span>Shipping</span><span>{money(order.shipping_amount)}</span></div><div className="flex justify-between border-t border-[var(--border)] pt-2 font-bold"><span>Total</span><span>{money(order.total)}</span></div></div></section><section className="lt-card mt-4"><h2 className="text-lg font-bold">Delivery</h2><p className="mt-3 text-sm text-[var(--text-secondary)]">{order.shipping_address.address}, {order.shipping_address.city}, {order.shipping_address.state} {order.shipping_address.postal_code}, {order.shipping_address.country}</p><p className="mt-4 text-sm font-semibold">{fulfillmentMessage}</p>{order.tracking_number && <p className="mt-2 text-sm text-[var(--text-secondary)]">{order.tracking_carrier ?? "Carrier"} · {order.tracking_number}{order.shipped_at ? ` · ${new Date(order.shipped_at).toLocaleDateString("en-IN")}` : ""}</p>}</section>{(order.cancelled_at || order.refund_status) && <section className="lt-card mt-4"><div className="flex items-center gap-2"><RotateCcw size={17} className="text-[var(--lt-accent-dark)]" /><h2 className="text-lg font-bold">Cancellation and refund</h2></div><p className="mt-3 text-sm text-[var(--text-secondary)]">{order.refund_message ?? (order.cancelled_at ? "Order cancelled." : "")}</p>{order.refund_amount != null && <p className="mt-2 text-sm font-semibold">Refund amount: {money(order.refund_amount)}</p>}</section>}{canCancel(order) && <button disabled={cancelling} onClick={() => void handleCancel()} className="lt-btn lt-btn-secondary mt-5">{cancelling ? "Cancelling..." : "Cancel Order"}</button>}{cancellationBlocked && !order.cancelled_at && <p className="mt-5 text-xs text-[var(--text-muted)]">Cancellation is unavailable after fulfillment has started.</p>}</main>;
}
