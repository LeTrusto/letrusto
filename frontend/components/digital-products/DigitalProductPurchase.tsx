"use client";

import Link from "next/link";
import Script from "next/script";
import { useState } from "react";
import { CheckCircle2, Download, Loader2, LockKeyhole } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { trackSafeEvent } from "@/lib/analytics";
import { createDigitalPaymentOrder, downloadDigitalProduct, verifyDigitalPayment } from "@/services/digitalProduct.service";
import { formatDigitalProductPrice } from "@/lib/digitalProducts";
import type { DigitalProduct } from "@/types/digital-products";
import type { RazorpayResult } from "@/lib/razorpayCheckout";

export default function DigitalProductPurchase({ product }: { product: DigitalProduct }) {
  const { accessToken, isAuthenticated, isLoading, user } = useAuth();
  const [state, setState] = useState<"idle" | "working" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  async function startCheckout() {
    if (!accessToken) return;
    trackSafeEvent("digital_product_cta_clicked", { product_name: product.name, product_slug: product.slug, interaction: "purchase_attempt" });
    setState("working"); setMessage("");
    try {
      const order = await createDigitalPaymentOrder(accessToken, product.slug);
      trackSafeEvent("digital_product_checkout_started", { product_name: product.name, product_slug: product.slug });
      if (!window.Razorpay) throw new Error("Secure checkout is still loading. Please try again.");
      const checkout = new window.Razorpay({ key: order.key_id, amount: order.amount, currency: order.currency, order_id: order.razorpay_order_id, name: "LeTrusto", description: product.name, prefill: { name: user?.full_name ?? "", email: user?.email ?? "", contact: "" }, handler: async (result: RazorpayResult) => {
        try { const purchase = await verifyDigitalPayment(accessToken, product.slug, result); trackSafeEvent("digital_product_payment_verified", { product_name: product.name, product_slug: product.slug }); if (purchase.status === "ACTIVE") { trackSafeEvent("digital_product_entitlement_created", { product_name: product.name, product_slug: product.slug }); trackSafeEvent("digital_product_purchase_completed", { product_name: product.name, product_slug: product.slug }); } setState("success"); setMessage("Payment verified. Your download is ready."); }
        catch (error) { setState("error"); setMessage(error instanceof Error ? error.message : "Payment verification failed."); }
      }, modal: { ondismiss: () => setState("idle") } });
      checkout.on?.("payment.failed", (failure) => { trackSafeEvent("digital_product_payment_failed", { product_name: product.name, product_slug: product.slug, failure_type: "gateway" }); setState("error"); setMessage(failure.error?.description ?? "Payment failed."); });
      trackSafeEvent("digital_product_payment_initiated", { product_name: product.name, product_slug: product.slug });
      checkout.open();
    } catch (error) { setState("error"); setMessage(error instanceof Error ? error.message : "Checkout could not be started."); }
  }

  async function download() {
    if (!accessToken) return;
    try { trackSafeEvent("digital_product_download_initiated", { product_name: product.name, product_slug: product.slug }); const blob = await downloadDigitalProduct(accessToken, product.slug); const url = URL.createObjectURL(blob); const anchor = document.createElement("a"); anchor.href = url; anchor.download = `${product.slug}.csv`; anchor.click(); URL.revokeObjectURL(url); trackSafeEvent("digital_product_download_completed", { product_name: product.name, product_slug: product.slug }); }
    catch (error) { setState("error"); setMessage(error instanceof Error ? error.message : "Download failed."); }
  }

  return <aside id="purchase" className="lt-card border-[var(--lt-primary)]"><Script src="https://checkout.razorpay.com/v1/checkout.js" strategy="afterInteractive" /><p className="lt-eyebrow">Digital delivery</p><div className="mt-3 flex items-end justify-between gap-4"><p className="text-3xl font-black text-[var(--text-primary)]">{formatDigitalProductPrice(product)}</p><span className="text-right text-xs font-semibold text-[var(--text-muted)]">One-time<br />purchase</span></div>{!isAuthenticated && !isLoading ? <div className="mt-6 border border-[var(--border)] bg-[var(--surface-soft)] p-4"><p className="flex items-center gap-2 text-sm font-bold text-[var(--text-primary)]"><LockKeyhole size={17} aria-hidden="true" /> Sign in to purchase</p><p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">Your download is attached to your LeTrusto account.</p><Link href={`/login?next=/digital-products/${product.slug}#purchase`} onClick={() => trackSafeEvent("digital_product_auth_required", { product_name: product.name, product_slug: product.slug })} className="lt-button-primary mt-4 inline-flex">Sign in</Link></div> : state === "success" ? <div className="mt-6 border border-emerald-700 bg-emerald-50 p-4" role="status"><p className="flex items-center gap-2 text-sm font-bold text-emerald-900"><CheckCircle2 size={17} aria-hidden="true" /> {message}</p><button type="button" onClick={download} className="lt-button-primary mt-4 inline-flex items-center gap-2"><Download size={16} aria-hidden="true" /> Download toolkit</button></div> : <div className="mt-6"><button type="button" onClick={startCheckout} disabled={state === "working" || isLoading} className="lt-button-primary inline-flex w-full items-center justify-center gap-2">{state === "working" && <Loader2 size={16} className="animate-spin" aria-hidden="true" />}{state === "working" ? "Preparing secure checkout" : "Buy toolkit"}</button>{message && <p className="mt-3 text-sm text-red-700" role="alert">{message}</p>}</div>}<p className="mt-4 text-xs leading-5 text-[var(--text-muted)]">Protected digital delivery. This product never enters the physical cart and does not use shipping or Printful fulfillment.</p></aside>;
}