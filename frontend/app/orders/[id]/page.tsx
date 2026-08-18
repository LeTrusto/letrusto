"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { getOrder } from "@/services/order.service";
import type { Order } from "@/types/orders";

function money(value: number) { return `₹${value.toLocaleString("en-IN")}`; }

export default function OrderConfirmationPage() {
  const { accessToken, isLoading } = useAuth();
  const params = useParams<{ id: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { if (!accessToken || !params.id) return; void getOrder(accessToken, params.id).then(setOrder).catch((err) => setError(err instanceof Error ? err.message : "Unable to load order")); }, [accessToken, params.id]);
  if (isLoading || !order && !error) return <main className="max-w-2xl mx-auto px-4 py-20 text-center">Loading order...</main>;
  if (error) return <main className="max-w-2xl mx-auto px-4 py-20 text-center"><p role="alert">{error}</p><Link href="/shop" className="lt-btn lt-btn-primary mt-6 inline-flex">Return to shop</Link></main>;
  if (!order) return null;
  return <main className="max-w-3xl mx-auto px-4 md:px-6 py-10"><div className="lt-card p-6"><p className="text-sm font-semibold text-[var(--lt-success)]">Order created</p><h1 className="lt-heading-2 mt-2">Thank you for your order</h1><p className="mt-2 text-sm text-[var(--text-secondary)]">Order number: <strong>{order.order_number}</strong></p><div className="mt-6 grid gap-3 sm:grid-cols-3 text-sm"><div><span className="text-[var(--text-muted)]">Total</span><p className="font-bold">{money(order.total)}</p></div><div><span className="text-[var(--text-muted)]">Payment</span><p className="font-bold">{order.payment_status}</p></div><div><span className="text-[var(--text-muted)]">Fulfillment</span><p className="font-bold">{order.fulfillment_status}</p></div></div><div className="mt-6 border-t border-[var(--border)] pt-5 space-y-3">{order.items.map((item) => <div key={item.id} className="flex justify-between text-sm"><span>{item.product_name} · {item.variant_name} × {item.quantity}</span><strong>{money(item.line_total)}</strong></div>)}</div><p className="mt-6 text-sm text-[var(--text-secondary)]">Payment is pending. No payment was charged and no supplier fulfillment was created.</p></div><Link href="/shop" className="lt-btn lt-btn-ghost mt-6 inline-flex">Continue Shopping</Link></main>;
}