import { buildApiUrl } from "@/services/api";
import type { CancellationStatus, CreateOrderPayload, Order, OrderList, PaymentSession, PaymentStatus, RazorpayOrder, StripeCheckoutSession } from "@/types/orders";

async function orderRequest<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildApiUrl(path), {
    ...init,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}`, ...(init?.headers ?? {}) },
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string | Array<{ msg?: string }> };
    const detail = Array.isArray(body.detail) ? body.detail.map((item) => item.msg ?? "Invalid value").join("; ") : body.detail;
    throw new Error(detail ?? `Order request failed (${response.status})`);
  }
  return (await response.json()) as T;
}

export function createOrder(token: string, payload: CreateOrderPayload) {
  return orderRequest<Order>("/orders", token, { method: "POST", body: JSON.stringify(payload) });
}

export function getOrder(token: string, orderId: string) {
  return orderRequest<Order>(`/orders/${orderId}`, token);
}

export function getAccountOrders(token: string, page = 1, pageSize = 20) {
  return orderRequest<OrderList>(`/account/orders?page=${page}&page_size=${pageSize}`, token);
}

export function cancelOrder(token: string, orderId: string, reason?: string) {
  return orderRequest<CancellationStatus>(`/orders/${orderId}/cancel`, token, {
    method: "POST",
    body: JSON.stringify({ reason: reason ?? "Customer requested cancellation" }),
  });
}

export function createCashfreeSession(token: string, orderId: string) {
  return orderRequest<PaymentSession>(`/orders/${orderId}/cashfree-session`, token, { method: "POST" });
}

export function verifyCashfreePayment(token: string, orderId: string) {
  return orderRequest<{ payment_status: string; order_status: string; fulfillment_status: string }>(`/orders/${orderId}/payment-status`, token);
}

export function createRazorpayOrder(token: string, orderId: string) {
  return orderRequest<RazorpayOrder>(`/orders/${orderId}/razorpay-order`, token, { method: "POST" });
}

export function verifyRazorpayPayment(token: string, orderId: string, payload: { razorpay_order_id: string; razorpay_payment_id: string; razorpay_signature: string }) {
  return orderRequest<PaymentStatus>(`/orders/${orderId}/razorpay/verify`, token, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function verifyRazorpayPaymentStatus(token: string, orderId: string) {
  return orderRequest<PaymentStatus>(`/orders/${orderId}/razorpay/payment-status`, token);
}

export function verifyPendingOrderPayment(token: string, order: Pick<Order, "id" | "payment_status" | "payment_provider">) {
  if (order.payment_status !== "PENDING") return Promise.resolve(null);
  if (order.payment_provider === "RAZORPAY") return verifyRazorpayPaymentStatus(token, order.id);
  if (order.payment_provider === "CASHFREE") return verifyCashfreePayment(token, order.id);
  return Promise.resolve(null);
}

export function createStripeSession(token: string, orderId: string) {
  return orderRequest<StripeCheckoutSession>(`/orders/${orderId}/stripe-session`, token, { method: "POST" });
}