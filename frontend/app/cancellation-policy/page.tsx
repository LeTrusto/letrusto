import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Cancellation Policy",
  description: "LeTrusto order cancellation eligibility and refund handling.",
  alternates: {
    canonical: "/cancellation-policy",
  },
};

export default function CancellationPolicyPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10 md:px-6 md:py-16">
      <h1 className="lt-heading-1">Cancellation Policy</h1>
      <p className="mt-3 text-sm text-[var(--text-muted)]">Last updated: 2026-08-31</p>

      <div className="lt-body mt-6 space-y-5">
        <section>
          <h2 className="lt-heading-3 mt-6">When cancellation may be possible</h2>
          <p>
            Because LeTrusto products are made to order, cancellation is only available while an order is still eligible and before production or fulfillment has started. Once an order has been submitted to a fulfillment partner, entered production, shipped, or delivered, cancellation may no longer be possible.
          </p>
        </section>

        <section>
          <h2 className="lt-heading-3 mt-6">How to request cancellation</h2>
          <p>
            Sign in to your account, open the order, and use the cancellation option if it is available. You can also contact LeTrusto support with your order number at <a className="underline" href="mailto:hello@letrusto.com">hello@letrusto.com</a> or through the <Link className="underline" href="/support?tab=contact&category=contact">Support Centre</Link>.
          </p>
        </section>

        <section>
          <h2 className="lt-heading-3 mt-6">Paid orders and refunds</h2>
          <p>
            If a paid order is approved for cancellation, LeTrusto will initiate the applicable refund through the original payment provider where supported. LeTrusto generally initiates approved refunds within approximately 5-7 business days where applicable, but the time for the amount to appear in your account may depend on Razorpay, your bank, card issuer, or other payment network processing.
          </p>
        </section>

        <section>
          <h2 className="lt-heading-3 mt-6">Cancellation is not guaranteed</h2>
          <p>
            A cancellation request does not guarantee cancellation. If production or fulfillment has already progressed, the order may continue and any issue after delivery will be reviewed under the <Link className="underline" href="/returns-policy">Returns &amp; Refunds Policy</Link>.
          </p>
        </section>
        <section>
          <h2 className="lt-heading-3 mt-6">Digital products and services</h2>
          <p>Digital products are delivered through a protected download after payment verification. A cancellation request is not available after access has been delivered, except where required by applicable law or where LeTrusto cannot provide the purchased file. A service enquiry is not an order, so there is no service booking or payment to cancel when an enquiry is submitted. Any separately agreed service terms will be shown before work begins.</p>
        </section>
      </div>
    </main>
  );
}
