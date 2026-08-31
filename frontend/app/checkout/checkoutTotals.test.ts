import { readFileSync } from "node:fs";
import { fileURLToPath, URL } from "node:url";

import { describe, expect, it } from "vitest";

const checkoutSource = readFileSync(fileURLToPath(new URL("./page.tsx", import.meta.url)), "utf8");
const cartSource = readFileSync(fileURLToPath(new URL("../cart/CartPageView.tsx", import.meta.url)), "utf8");

describe("checkout totals contract", () => {
  it("renders shipping and total from the server quote", () => {
    expect(checkoutSource).toContain("money(quote!.shipping_amount)");
    expect(checkoutSource).toContain("money(quote!.total)");
    expect(checkoutSource).toContain("createdOrder.shipping_amount");
    expect(checkoutSource).toContain("money(createdOrder.total)");
  });

  it("never presents shipping as included in the product price", () => {
    expect(checkoutSource).not.toContain("Included in total");
    expect(cartSource).not.toContain("Included in total");
    expect(cartSource).toContain("Calculated at checkout");
  });

  it("does not compute the payable total on the client", () => {
    expect(checkoutSource).not.toMatch(/subtotal\s*\+\s*ship/i);
    expect(checkoutSource).not.toContain("NEXT_PUBLIC_PRICING_FX_RATE");
    expect(checkoutSource).not.toContain("INR_PER_USD");
  });

  it("keeps checkout on INR and blocks unsupported international payment", () => {
    expect(checkoutSource).not.toContain('"USD"');
    expect(checkoutSource).toContain("International checkout is not available yet");
    expect(checkoutSource).toContain("only for India shipping addresses");
  });

  it("disables payment until the server confirms a purchasable quote", () => {
    expect(checkoutSource).toContain("const serverTotalsReady = quoteState === \"ready\" && quote !== null && quote.purchasable");
    expect(checkoutSource).toContain("disabled={working || !serverTotalsReady}");
  });

  it("uses Razorpay as the only payment provider", () => {
    expect(checkoutSource).toContain("Razorpay");
    expect(checkoutSource).not.toContain("Stripe");
  });

  it("shows the available legal policies before payment", () => {
    for (const href of ["/terms-of-use", "/privacy-policy", "/shipping-policy", "/returns-policy"]) {
      expect(checkoutSource).toContain(href);
    }
  });
});
