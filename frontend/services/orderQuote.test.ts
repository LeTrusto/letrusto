import { describe, expect, it, vi } from "vitest";

import { getOrderQuote } from "@/services/order.service";
import { toCommerceProduct } from "@/services/product.service";
import type { Product } from "@/types/products";

const quote = {
  currency: "INR",
  subtotal: 8998,
  shipping_amount: 399,
  total: 9397,
  shipping_status: "AVAILABLE",
  shipping_message: "Estimated shipping; pending Printful verification",
  purchasable: true,
  unavailable_reason: null,
};

function hoodie(): Product {
  return {
    id: "hoodie",
    name: "Unisex Hoodie",
    description: "Hoodie",
    priceValue: 4499,
    images: [],
    category: "apparel",
    tags: [],
    variants: [],
    priceHistory: [],
    reviews: [],
    rating: 0,
    aiScore: 0,
  } as unknown as Product;
}

describe("checkout order quote", () => {
  it("requests the server-authoritative quote with authentication", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(quote), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    const result = await getOrderQuote("access-token", {
      items: [{ product_id: "hoodie", variant_id: "variant-1", quantity: 2 }],
      country: "IN",
    });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/orders/quote"),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ Authorization: "Bearer access-token" }),
        body: JSON.stringify({ items: [{ product_id: "hoodie", variant_id: "variant-1", quantity: 2 }], country: "IN" }),
      }),
    );
    expect(result.subtotal + result.shipping_amount).toBe(result.total);
  });

  it("keeps the quote currency and totals exactly as returned by the server", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(quote), { status: 200 })));

    const result = await getOrderQuote("access-token", { items: [], country: "IN" });

    expect(result.currency).toBe("INR");
    expect(result.shipping_amount).toBe(399);
    expect(result.total).toBe(9397);
  });

  it("surfaces an unsupported international destination as not purchasable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({
      ...quote,
      shipping_amount: 0,
      total: 8998,
      shipping_status: "UNAVAILABLE",
      purchasable: false,
      unavailable_reason: "INTERNATIONAL_CHECKOUT_UNAVAILABLE",
    }), { status: 200 })));

    const result = await getOrderQuote("access-token", { items: [], country: "US" });

    expect(result.purchasable).toBe(false);
    expect(result.unavailable_reason).toBe("INTERNATIONAL_CHECKOUT_UNAVAILABLE");
    expect(result.currency).toBe("INR");
  });

  it("propagates a server shipping failure instead of assuming zero shipping", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Shipping could not be calculated." }), { status: 400 })));

    await expect(getOrderQuote("access-token", { items: [], country: "IN" })).rejects.toThrow("Shipping could not be calculated.");
  });

  it("prices catalog products in INR through the whole checkout path", () => {
    expect(toCommerceProduct(hoodie()).currency).toBe("INR");
  });
});
