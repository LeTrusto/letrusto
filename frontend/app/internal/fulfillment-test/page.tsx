"use client";

import Link from "next/link";
import DigitalProductPurchase from "@/components/digital-products/DigitalProductPurchase";
import { useAuth } from "@/hooks/useAuth";
import type { DigitalProduct } from "@/types/digital-products";

const testProduct: DigitalProduct = {
  id: "internal-fulfillment-test-toolkit", name: "LeTrusto Fulfillment Test Toolkit", slug: "letrusto-fulfillment-test-toolkit",
  description: "Internal production checkout and protected delivery verification.", valueProposition: "A real ₹1 transaction for validating the full digital delivery path.",
  category: { slug: "internal", name: "Internal test", description: "" }, format: "Editable CSV", price: 1, currency: "INR", previewLabel: "Internal test asset",
  included: ["Protected download", "Account entitlement", "Purchase email"], audience: ["LeTrusto owner"], usage: ["Production fulfillment verification"], status: "draft", delivery: "protected-download", assetVersion: "1.0", faq: [],
};

export default function FulfillmentTestPage() {
  const { isAdmin, isLoading, isAuthenticated } = useAuth();
  if (isLoading) return <main className="mx-auto max-w-3xl px-4 py-16">Loading...</main>;
  if (!isAuthenticated || !isAdmin) return <main className="mx-auto max-w-3xl px-4 py-16"><h1 className="lt-heading-2">Internal access required</h1><p className="lt-body mt-3">This fulfillment test is available only to an authenticated LeTrusto admin.</p><Link href="/login?next=/internal/fulfillment-test" className="lt-btn-primary lt-btn-md mt-6 inline-flex">Sign in</Link></main>;
  return <main className="mx-auto max-w-3xl px-4 py-12"><p className="lt-eyebrow">Internal fulfillment test</p><h1 className="lt-heading-1 mt-3">{testProduct.name}</h1><p className="lt-body mt-4">This private page uses the production Razorpay, verification, entitlement, email, and protected download pipeline.</p><div className="mt-8 max-w-md"><DigitalProductPurchase product={testProduct} /></div></main>;
}