import { readFileSync } from "node:fs";
import { fileURLToPath, URL } from "node:url";

import { describe, expect, it } from "vitest";

const checkoutSource = readFileSync(fileURLToPath(new URL("./page.tsx", import.meta.url)), "utf8");

describe("retired physical checkout contract", () => {
  it("renders the explicit paused state", () => {
    expect(checkoutSource).toContain("PhysicalCommercePaused");
    expect(checkoutSource).toContain("Checkout");
  });

  it("does not expose physical payment or quote behavior", () => {
    expect(checkoutSource).not.toContain("Razorpay");
    expect(checkoutSource).not.toContain("getOrderQuote");
    expect(checkoutSource).not.toContain("createOrder");
    expect(checkoutSource).not.toContain("Stripe");
  });
});
