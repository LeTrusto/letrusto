import { describe, expect, it, vi } from "vitest";

import { verifyPendingOrderPayment } from "@/services/order.service";

const response = { order_id: "order-1", payment_status: "PAID", order_status: "PAID", fulfillment_status: "PENDING", provider_reference: "pay-1" };

describe("order-detail payment verification", () => {
  it("uses Razorpay verification for a pending Razorpay order", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(response), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await verifyPendingOrderPayment("token", { id: "order-1", payment_status: "PENDING", payment_provider: "RAZORPAY" });

    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/orders/order-1/razorpay/payment-status"), expect.anything());
    expect(fetchMock).not.toHaveBeenCalledWith(expect.stringContaining("cashfree"), expect.anything());
  });

  it("retains Cashfree verification for a pending Cashfree order", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(response), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await verifyPendingOrderPayment("token", { id: "order-1", payment_status: "PENDING", payment_provider: "CASHFREE" });

    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/orders/order-1/payment-status"), expect.anything());
    expect(fetchMock.mock.calls[0][0]).not.toContain("razorpay");
  });

  it("does not verify a completed Razorpay order", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await verifyPendingOrderPayment("token", { id: "order-1", payment_status: "PAID", payment_provider: "RAZORPAY" });

    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("preserves provider verification failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Razorpay payment status could not be verified" }), { status: 400 })));

    await expect(verifyPendingOrderPayment("token", { id: "order-1", payment_status: "PENDING", payment_provider: "RAZORPAY" })).rejects.toThrow("Razorpay payment status could not be verified");
  });
});