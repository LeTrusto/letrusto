"use client";

import Link from "next/link";
import Script from "next/script";
import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useCart } from "@/lib/cartContext";
import { createCashfreeSession, createOrder } from "@/services/order.service";
import type { Order, PaymentSession } from "@/types/orders";
import { getPublicProducts, toCommerceProduct } from "@/services/product.service";

function money(value: number) { return `₹${value.toLocaleString("en-IN")}`; }

export default function CheckoutPage() {
  const { accessToken, isLoading, isAuthenticated, user } = useAuth();
  const { items, subtotal } = useCart();
  const [products, setProducts] = useState<Record<string, ReturnType<typeof toCommerceProduct>>>({});
  const [form, setForm] = useState({ name: user?.full_name ?? "", email: user?.email ?? "", phone: "", address: "", city: "", state: "", postal_code: "", country: "IN" });
  const [error, setError] = useState("");
  const [working, setWorking] = useState(false);
  const [createdOrder, setCreatedOrder] = useState<Order | null>(null);
  const [paymentSession, setPaymentSession] = useState<PaymentSession | null>(null);

  useEffect(() => {
    void getPublicProducts().then((catalog) => {
      setProducts(Object.fromEntries(catalog.map((item) => {
        const product = toCommerceProduct(item);
        return [product.id, product];
      })));
    }).catch(() => {});
  });

  if (isLoading) return <main className="max-w-2xl mx-auto px-4 py-20 text-center">Loading checkout...</main>;
  if (!isAuthenticated) return <main className="max-w-2xl mx-auto px-4 py-20 text-center"><h1 className="lt-heading-2">Sign in to checkout</h1><p className="mt-2 text-sm text-[var(--text-secondary)]">Your cart is ready. Sign in to create a pending-payment order.</p><Link href="/login?redirect=/checkout" className="lt-btn lt-btn-primary mt-6 inline-flex">Sign In</Link></main>;
  if (items.length === 0) return <main className="max-w-2xl mx-auto px-4 py-20 text-center"><h1 className="lt-heading-2">Your cart is empty</h1><Link href="/shop" className="lt-btn lt-btn-primary mt-6 inline-flex">Continue Shopping</Link></main>;

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!accessToken) return;
    setWorking(true); setError("");
    try {
      const order = await createOrder(accessToken, {
        items: items.map((item) => ({
          product_id: item.productId,
          variant_id: item.selectedVariantId ?? "",
          quantity: item.quantity,
        })),
        customer: { name: form.name, email: form.email, phone: form.phone },
        shipping_address: { address: form.address, city: form.city, state: form.state, postal_code: form.postal_code, country: form.country },
        idempotency_key: `checkout-${crypto.randomUUID()}`,
      });
      setCreatedOrder(order);
      try {
        const session = await createCashfreeSession(accessToken, order.id);
        setPaymentSession(session);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Cashfree payment session unavailable");
      }
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to create order"); }
    finally { setWorking(false); }
  }

  const update = (field: keyof typeof form) => (event: React.ChangeEvent<HTMLInputElement>) => setForm((current) => ({ ...current, [field]: event.target.value }));
  async function openCashfree() {
    if (!paymentSession) return;
    const cashfree = (window as Window & { Cashfree?: (options: { mode: "sandbox" | "production" }) => { checkout: (options: { paymentSessionId: string; redirectTarget: string }) => Promise<unknown> } }).Cashfree;
    if (!cashfree) { setError("Cashfree checkout is unavailable. Configure the sandbox payment script and credentials."); return; }
    await cashfree({ mode: "sandbox" }).checkout({ paymentSessionId: paymentSession.payment_session_id, redirectTarget: "_self" });
  }

  if (createdOrder) return <main className="max-w-2xl mx-auto px-4 py-20 text-center"><h1 className="lt-heading-2">Order ready for payment</h1><p className="mt-2 text-sm text-[var(--text-secondary)]">Order {createdOrder.order_number} is still pending payment.</p>{paymentSession ? <button onClick={() => { void openCashfree(); }} className="lt-btn lt-btn-primary mt-6">Open Cashfree Payment</button> : <p role="alert" className="mt-6 text-sm text-[var(--lt-rose)]">{error || "Cashfree sandbox credentials are not configured."}</p>}<Link href={`/orders/${createdOrder.id}`} className="lt-btn lt-btn-ghost mt-4 inline-flex">View pending order</Link></main>;

  return <><Script src="https://sdk.cashfree.com/js/v3/cashfree.js" strategy="afterInteractive" /><main className="max-w-6xl mx-auto px-4 md:px-6 py-8">
    <h1 className="lt-heading-2">Checkout</h1><p className="mt-1 text-sm text-[var(--text-muted)]">Your order will remain pending until payment integration is available.</p>
    <form onSubmit={(event) => { void submit(event); }} className="mt-6 grid gap-8 lg:grid-cols-[1fr_22rem]">
      <section className="space-y-6">
        <div className="lt-card p-5"><h2 className="font-bold">Customer details</h2><div className="mt-4 grid gap-4 sm:grid-cols-2">
          <label className="lt-label">Name<input required value={form.name} onChange={update("name")} className="lt-input mt-1" /></label>
          <label className="lt-label">Email<input required type="email" value={form.email} onChange={update("email")} className="lt-input mt-1" /></label>
          <label className="lt-label sm:col-span-2">Phone<input required value={form.phone} onChange={update("phone")} className="lt-input mt-1" /></label>
        </div></div>
        <div className="lt-card p-5"><h2 className="font-bold">Shipping address</h2><div className="mt-4 grid gap-4 sm:grid-cols-2">
          <label className="lt-label sm:col-span-2">Address<input required value={form.address} onChange={update("address")} className="lt-input mt-1" /></label>
          <label className="lt-label">City<input required value={form.city} onChange={update("city")} className="lt-input mt-1" /></label>
          <label className="lt-label">State<input required value={form.state} onChange={update("state")} className="lt-input mt-1" /></label>
          <label className="lt-label">Postal code<input required value={form.postal_code} onChange={update("postal_code")} className="lt-input mt-1" /></label>
          <label className="lt-label">Country<input required value={form.country} onChange={update("country")} className="lt-input mt-1" /></label>
        </div></div>
        {error && <p role="alert" className="border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      </section>
      <aside className="lt-card h-fit p-5"><h2 className="font-bold">Order summary</h2><div className="mt-4 space-y-3 text-sm">{items.map((item) => { const product = products[item.productId]; const variant = product?.catalogVariants?.find((candidate) => candidate.id === item.selectedVariantId); const unitPrice = variant?.price ?? product?.price ?? 0; return <div key={`${item.productId}-${item.selectedVariantId}`} className="flex justify-between gap-3"><span>{product?.name ?? item.productId}<br /><span className="text-xs text-[var(--text-muted)]">{variant?.label ?? "Selected variant"} × {item.quantity} · {money(unitPrice)} each</span></span><strong>{money(unitPrice * item.quantity)}</strong></div>; })}</div><div className="mt-5 flex justify-between border-t border-[var(--border)] pt-4 font-bold"><span>Total</span><span>{money(subtotal)}</span></div><button disabled={working} className="lt-btn lt-btn-primary mt-5 w-full">{working ? "Creating order..." : "Place Order"}</button></aside>
    </form>
  </main></>;
}