"use client";

import Link from "next/link";
import Script from "next/script";
import { useEffect, useState } from "react";
import { CheckCircle2, Loader2, LockKeyhole } from "lucide-react";

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
  const [openingPayment, setOpeningPayment] = useState(false);
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
    if (!accessToken || working || createdOrder) return;
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
    if (!paymentSession || openingPayment) return;
    setOpeningPayment(true);
    setError("");
    const cashfree = (window as Window & { Cashfree?: (options: { mode: "sandbox" | "production" }) => { checkout: (options: { paymentSessionId: string; redirectTarget: string }) => Promise<unknown> } }).Cashfree;
    if (!cashfree) { setError("Payment checkout is unavailable. Please try again later."); setOpeningPayment(false); return; }
    try { await cashfree({ mode: "sandbox" }).checkout({ paymentSessionId: paymentSession.payment_session_id, redirectTarget: "_self" }); } catch { setError("Unable to open payment checkout. Please try again."); setOpeningPayment(false); }
  }

  if (createdOrder) return <main className="mx-auto max-w-2xl px-4 py-16 text-center md:py-20"><div className="lt-card p-6 md:p-8"><CheckCircle2 className="mx-auto text-[var(--lt-success)]" size={38} /><p className="lt-label mt-4">Order created</p><h1 className="lt-heading-2 mt-2">Ready for payment</h1><p className="mt-2 text-sm text-[var(--text-secondary)]">Order {createdOrder.order_number} is pending payment. Your order is confirmed only after the payment provider verifies it.</p>{paymentSession ? <button type="button" disabled={openingPayment} onClick={() => { void openCashfree(); }} className="lt-btn lt-btn-primary mt-6 w-full">{openingPayment ? <><Loader2 size={16} className="animate-spin" /> Opening payment...</> : "Continue to secure payment"}</button> : <p role="alert" className="mt-6 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error || "Payment checkout is unavailable for this order."}</p>}<Link href={`/orders/${createdOrder.id}`} className="lt-btn lt-btn-ghost mt-3 inline-flex">View order details</Link></div></main>;

  return <><Script src="https://sdk.cashfree.com/js/v3/cashfree.js" strategy="afterInteractive" /><main className="mx-auto max-w-6xl px-4 py-6 md:px-6 md:py-10">
    <header><p className="lt-label">Secure checkout</p><h1 className="lt-heading-2 mt-1">Checkout</h1><p className="mt-2 text-sm text-[var(--text-muted)]">Review your details before continuing to payment.</p></header>
    <form onSubmit={(event) => { void submit(event); }} className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_22rem] lg:gap-8">
      <section className="space-y-6">
        <div className="lt-card p-5"><div className="flex items-baseline justify-between gap-3"><h2 className="font-bold">Contact information</h2><span className="text-xs text-[var(--text-muted)]">Required</span></div><div className="mt-4 grid gap-4 sm:grid-cols-2">
          <label className="lt-label">Name <span aria-hidden="true">*</span><input required autoComplete="name" value={form.name} onChange={update("name")} className="lt-input mt-1" /></label>
          <label className="lt-label">Email <span aria-hidden="true">*</span><input required type="email" autoComplete="email" value={form.email} onChange={update("email")} className="lt-input mt-1" /></label>
          <label className="lt-label sm:col-span-2">Phone <span aria-hidden="true">*</span><input required type="tel" autoComplete="tel" inputMode="tel" value={form.phone} onChange={update("phone")} className="lt-input mt-1" /></label>
        </div></div>
        <div className="lt-card p-5"><div className="flex items-baseline justify-between gap-3"><h2 className="font-bold">Shipping address</h2><span className="text-xs text-[var(--text-muted)]">Required</span></div><div className="mt-4 grid gap-4 sm:grid-cols-2">
          <label className="lt-label sm:col-span-2">Address <span aria-hidden="true">*</span><input required autoComplete="street-address" value={form.address} onChange={update("address")} className="lt-input mt-1" /></label>
          <label className="lt-label">City <span aria-hidden="true">*</span><input required autoComplete="address-level2" value={form.city} onChange={update("city")} className="lt-input mt-1" /></label>
          <label className="lt-label">State <span aria-hidden="true">*</span><input required autoComplete="address-level1" value={form.state} onChange={update("state")} className="lt-input mt-1" /></label>
          <label className="lt-label">Postal code <span aria-hidden="true">*</span><input required autoComplete="postal-code" inputMode="numeric" value={form.postal_code} onChange={update("postal_code")} className="lt-input mt-1" /></label>
          <label className="lt-label">Country <span aria-hidden="true">*</span><input required autoComplete="country" value={form.country} onChange={update("country")} className="lt-input mt-1" /></label>
        </div></div>
        {error && <p role="alert" className="border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      </section>
      <aside className="lt-card h-fit p-5 lg:sticky lg:top-20"><h2 className="font-bold">Order summary</h2><div className="mt-4 space-y-4 text-sm">{items.map((item) => { const product = products[item.productId]; const variant = product?.catalogVariants?.find((candidate) => candidate.id === item.selectedVariantId); const unitPrice = variant?.price ?? product?.price ?? 0; return <div key={`${item.productId}-${item.selectedVariantId}`} className="flex justify-between gap-3"><span className="min-w-0"><span className="line-clamp-2 font-medium">{product?.name ?? item.productId}</span><span className="mt-1 block text-xs text-[var(--text-muted)]">{variant?.label ?? "Selected variant"} · {item.quantity} × {money(unitPrice)}</span></span><strong className="shrink-0">{money(unitPrice * item.quantity)}</strong></div>; })}</div><div className="mt-5 space-y-2 border-t border-[var(--border)] pt-4 text-sm"><div className="flex justify-between"><span className="text-[var(--text-secondary)]">Subtotal</span><span>{money(subtotal)}</span></div><div className="flex justify-between"><span className="text-[var(--text-secondary)]">Shipping</span><span>Included in total</span></div></div><div className="mt-4 flex justify-between border-t border-[var(--border)] pt-4 text-base font-bold"><span>Total</span><span>{money(subtotal)}</span></div><button disabled={working} className="lt-btn lt-btn-primary mt-5 w-full">{working ? <><Loader2 size={16} className="animate-spin" /> Creating order...</> : "Continue to payment"}</button><p className="mt-3 flex items-start gap-2 text-xs text-[var(--text-muted)]"><LockKeyhole size={14} className="mt-0.5 shrink-0" />Payment is completed with the available payment provider after your order is created.</p></aside>
    </form>
  </main></>;
}