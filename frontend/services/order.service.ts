import { buildApiUrl } from "@/services/api";
import type { CreateOrderPayload, Order } from "@/types/orders";

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