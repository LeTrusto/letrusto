import { describe, expect, it, vi } from "vitest";

import { buildRazorpayCheckoutOptions, callbackMatchesOrder, isBackendPaymentSuccess, RAZORPAY_CHECKOUT_SCRIPT_URL } from "@/lib/razorpayCheckout";
import { createRazorpayOrder, verifyRazorpayPayment } from "@/services/order.service";
import type { RazorpayOrder } from "@/types/orders";

const paymentOrder: RazorpayOrder = {
  order_id: "letrusto-order",
  provider: "RAZORPAY",
  key_id: "rzp_test_public",
  razorpay_order_id: "order_test_123",
  amount: 41272,
  currency: "INR",
};

describe("Razorpay checkout boundary", () => {
  it("loads the official Razorpay Checkout script", () => {
    expect(RAZORPAY_CHECKOUT_SCRIPT_URL).toBe("https://checkout.razorpay.com/v1/checkout.js");
  });

  it("opens with the server-created amount, order, currency, and public key only", () => {
    const options = buildRazorpayCheckoutOptions(paymentOrder, "LT-123", { name: "Buyer", email: "buyer@example.com", contact: "9876543210" }, vi.fn(), vi.fn());

    expect(options).toMatchObject({ key: "rzp_test_public", amount: 41272, currency: "INR", order_id: "order_test_123" });
    expect(options).not.toHaveProperty("key_secret");
    expect(options).not.toHaveProperty("webhook_secret");
  });

  it("keeps success behind the backend PAID response", () => {
    expect(isBackendPaymentSuccess("PAID")).toBe(true);
    expect(isBackendPaymentSuccess("PENDING")).toBe(false);
    expect(isBackendPaymentSuccess("SUCCESS")).toBe(false);
  });

  it("rejects a callback for another Razorpay order", () => {
    expect(callbackMatchesOrder({ razorpay_order_id: "order_test_123", razorpay_payment_id: "pay_1", razorpay_signature: "sig" }, paymentOrder)).toBe(true);
    expect(callbackMatchesOrder({ razorpay_order_id: "order_other", razorpay_payment_id: "pay_1", razorpay_signature: "sig" }, paymentOrder)).toBe(false);
  });

  it("requests a server-created Razorpay order with authentication", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(paymentOrder), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await createRazorpayOrder("access-token", "letrusto-order");
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/api/v1/orders/letrusto-order/razorpay-order"), expect.objectContaining({ method: "POST", headers: expect.objectContaining({ Authorization: "Bearer access-token" }) }));
  });

  it("sends Razorpay callback values to backend verification", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ payment_status: "PAID" }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const callback = { razorpay_order_id: "order_test_123", razorpay_payment_id: "pay_1", razorpay_signature: "sig_1" };
    await verifyRazorpayPayment("access-token", "letrusto-order", callback);
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/api/v1/orders/letrusto-order/razorpay/verify"), expect.objectContaining({ body: JSON.stringify(callback) }));
  });

  it("preserves distinct callback, cancellation, and failure handlers", () => {
    const handler = vi.fn();
    const ondismiss = vi.fn();
    const options = buildRazorpayCheckoutOptions(paymentOrder, "LT-123", { name: "Buyer", email: "buyer@example.com", contact: "9876543210" }, handler, ondismiss);

    expect(options.handler).toBe(handler);
    expect(options.modal.ondismiss).toBe(ondismiss);
  });
});