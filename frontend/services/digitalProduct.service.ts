import { authenticatedApiRequest, buildApiUrl } from "@/services/api";

export type DigitalPaymentOrder = {
  attempt_id: string;
  product_slug: string;
  provider: "RAZORPAY";
  key_id: string;
  razorpay_order_id: string;
  amount: number;
  currency: "INR";
};

export type DigitalPurchase = {
  product_slug: string;
  status: string;
  download_url: string | null;
  amount: string;
  currency: string;
};

export type DigitalEntitlement = {
  product_slug: string;
  product_name: string;
  status: string;
  amount: string;
  currency: string;
  download_url: string;
  purchased_at: string;
};

export function createDigitalPaymentOrder(token: string, slug: string) {
  return authenticatedApiRequest<DigitalPaymentOrder>(token, `/digital-products/${slug}/payment-order`, { method: "POST" });
}

export function verifyDigitalPayment(token: string, slug: string, payload: { razorpay_order_id: string; razorpay_payment_id: string; razorpay_signature: string }) {
  return authenticatedApiRequest<DigitalPurchase>(token, `/digital-products/${slug}/verify`, { method: "POST", body: JSON.stringify(payload) });
}

export async function downloadDigitalProduct(token: string, slug: string) {
  const response = await fetch(buildApiUrl(`/digital-products/${slug}/download`), { headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) throw new Error("The download could not be prepared.");
  return response.blob();
}

export function getDigitalPurchases(token: string) {
  return authenticatedApiRequest<DigitalEntitlement[]>(token, "/account/digital-purchases");
}
