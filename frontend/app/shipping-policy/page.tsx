import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Shipping Policy",
  description: "LeTrusto shipping information and delivery timelines.",
};

export default function ShippingPolicyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 md:px-6 py-10 md:py-16">
      <h1 className="lt-heading-1">Shipping Policy</h1>
      <p className="mt-3 text-sm text-[var(--text-muted)]">Last updated: 2026-08-31</p>
      <div className="mt-6 lt-body space-y-4">
        <h2 className="lt-heading-3 mt-6">Current purchasing destination</h2>
        <p>India is the active purchasing destination for launch. International visitors may browse products, but international checkout and international purchasing are currently unavailable.</p>
        <h2 className="lt-heading-3 mt-6">Delivery</h2>
        <p>Each product is made to order after purchase. Production and delivery timing can vary by product, fulfillment capacity, destination, carrier, and events outside LeTrusto&apos;s control. Tracking is provided where available after the order has been produced and handed to the carrier.</p>
        <h2 className="lt-heading-3 mt-6">Shipping Charges</h2>
        <p>Shipping is charged separately from the product price. Checkout uses the server-authoritative shipping calculation and includes shipping as a separate component in the final payable total before Razorpay payment.</p>
        <p>The current India hoodie launch estimate is ₹299 for the first hoodie and ₹100 for each additional hoodie in the same order. This is a LeTrusto estimate for Printful shipping and is marked as requiring Printful verification. The estimate may be updated before or after launch if Printful rates or fulfillment constraints change.</p>
        <h2 className="lt-heading-3 mt-6">Unsupported addresses</h2>
        <p>If checkout cannot confirm shipping for an address, the order cannot proceed to payment. Please check the address or contact support through the <Link className="underline" href="/support?tab=contact&category=contact">Support Centre</Link>.</p>
        <h2 className="lt-heading-3 mt-6">Tracking</h2>
        <p>You will receive tracking information by email once your order has been produced and handed to the carrier. Tracking updates may take a few days to appear.</p>
        <h2 className="lt-heading-3 mt-6">Delivery Issues</h2>
        <p>If an order is delayed, lost, or arrives damaged, contact us through the Support Centre with your order number and photographs where relevant. We will investigate with the fulfillment and delivery partners.</p>
      </div>
    </div>
  );
}
