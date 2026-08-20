import type { RazorpayOrder } from "@/types/orders";

export const RAZORPAY_CHECKOUT_SCRIPT_URL = "https://checkout.razorpay.com/v1/checkout.js";

export type RazorpayResult = {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
};

export type RazorpayPaymentFailure = { error?: { description?: string } };

export type RazorpayCheckoutOptions = {
  key: string;
  amount: number;
  currency: string;
  order_id: string;
  name: string;
  description: string;
  prefill: { name: string; email: string; contact: string };
  handler: (response: RazorpayResult) => void;
  modal: { ondismiss: () => void };
};

export function buildRazorpayCheckoutOptions(
  paymentOrder: RazorpayOrder,
  orderNumber: string,
  prefill: RazorpayCheckoutOptions["prefill"],
  handler: RazorpayCheckoutOptions["handler"],
  ondismiss: () => void,
): RazorpayCheckoutOptions {
  return {
    key: paymentOrder.key_id,
    amount: paymentOrder.amount,
    currency: paymentOrder.currency,
    order_id: paymentOrder.razorpay_order_id,
    name: "LeTrusto",
    description: `Order ${orderNumber}`,
    prefill,
    handler,
    modal: { ondismiss },
  };
}

export function callbackMatchesOrder(response: RazorpayResult, paymentOrder: RazorpayOrder): boolean {
  return response.razorpay_order_id === paymentOrder.razorpay_order_id;
}

export function isBackendPaymentSuccess(paymentStatus: string): boolean {
  return paymentStatus === "PAID";
}
