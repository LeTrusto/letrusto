"use client";

import Script from "next/script";
import { Check, Loader2, X } from "lucide-react";
import { useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { createSubscription } from "@/services/saas.service";

const checkoutScript = "https://checkout.razorpay.com/v1/checkout.js";

type Props = { open: boolean; onClose: () => void };

type RazorpayPaymentFailure = { error?: { description?: string } };
type RazorpayInstance = { open: () => void; on?: (event: string, handler: (failure: RazorpayPaymentFailure) => void) => void };
type RazorpayConstructor = new (options: Record<string, unknown>) => RazorpayInstance;

declare global {
  interface Window { Razorpay?: RazorpayConstructor }
}

export default function UpgradePlanModal({ open, onClose }: Props) {
  const { user, accessToken } = useAuth();
  const [plan, setPlan] = useState<"starter" | "pro">("starter");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  if (!open) return null;

  async function beginCheckout() {
    if (!accessToken || !user) {
      setMessage("Please sign in before upgrading your plan.");
      return;
    }
    if (!window.Razorpay) {
      setMessage("Razorpay Checkout is still loading. Try again in a moment.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const checkout = await createSubscription(accessToken, plan);
      const razorpay = new window.Razorpay({
        key: checkout.key_id,
        subscription_id: checkout.subscription_id,
        name: "LeTrusto",
        description: `${plan === "pro" ? "Pro" : "Starter"} Social Proof plan`,
        prefill: { name: user.full_name, email: user.email ?? "" },
        theme: { color: "#e11d48" },
        handler: () => {
          setMessage("Checkout complete. Your plan will activate when Razorpay confirms the subscription.");
          setBusy(false);
        },
        modal: { ondismiss: () => setBusy(false) },
      });
      razorpay.open();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to start checkout.");
      setBusy(false);
    }
  }

  return (
    <>
      <Script src={checkoutScript} strategy="afterInteractive" />
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#10231dcc] px-4 py-8" role="dialog" aria-modal="true" aria-labelledby="upgrade-title">
        <div className="w-full max-w-lg border border-[#d5e0db] bg-[#fbfdfc] p-6 shadow-2xl sm:p-8">
          <div className="flex items-start justify-between gap-4">
            <div><p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#e11d48]">Scale your trust layer</p><h2 id="upgrade-title" className="mt-2 text-2xl font-black text-[#17382e]">Choose a plan</h2></div>
            <button type="button" onClick={onClose} className="rounded-full p-2 text-[#71877f] hover:bg-[#e8f0ec]" aria-label="Close upgrade modal"><X className="h-5 w-5" /></button>
          </div>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {(["starter", "pro"] as const).map((option) => (
              <button key={option} type="button" onClick={() => setPlan(option)} className={`border p-4 text-left transition ${plan === option ? "border-[#e11d48] bg-[#fff2f4]" : "border-[#d5e0db] bg-white hover:border-[#9db7aa]"}`}>
                <div className="flex items-center justify-between"><span className="font-bold capitalize text-[#17382e]">{option}</span>{plan === option && <Check className="h-4 w-4 text-[#e11d48]" />}</div>
                <p className="mt-2 text-xl font-black text-[#17382e]">{option === "starter" ? "₹999" : "₹2,499"}<span className="text-xs font-medium text-[#71877f]"> / month</span></p>
                <p className="mt-2 text-xs leading-5 text-[#587268]">{option === "starter" ? "3 widgets · 10,000 views" : "Unlimited widgets · video reviews"}</p>
              </button>
            ))}
          </div>
          {message && <p className="mt-4 border border-[#f6c5cf] bg-[#fff4f5] px-3 py-2 text-sm text-[#a31835]" role="alert">{message}</p>}
          <button type="button" onClick={beginCheckout} disabled={busy} className="mt-6 flex w-full items-center justify-center gap-2 bg-[#e11d48] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#be123c] disabled:cursor-wait disabled:opacity-60">
            {busy && <Loader2 className="h-4 w-4 animate-spin" />} Continue to secure checkout
          </button>
          <p className="mt-3 text-center text-xs text-[#71877f]">Recurring billing is handled securely by Razorpay.</p>
        </div>
      </div>
    </>
  );
}
