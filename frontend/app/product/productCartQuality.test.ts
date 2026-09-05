import { readFileSync } from "node:fs";
import { fileURLToPath, URL } from "node:url";

import { describe, expect, it } from "vitest";

const productSource = readFileSync(fileURLToPath(new URL("./[slug]/ProductDetailView.tsx", import.meta.url)), "utf8");
const cartSource = readFileSync(fileURLToPath(new URL("../cart/CartPageView.tsx", import.meta.url)), "utf8");
const cardSource = readFileSync(fileURLToPath(new URL("../../components/products/CommerceProductCard.tsx", import.meta.url)), "utf8");
const checkoutSource = readFileSync(fileURLToPath(new URL("../checkout/page.tsx", import.meta.url)), "utf8");

describe("product and cart production contracts", () => {
  it("keeps physical checkout paused during the B2B SaaS transition", () => {
    expect(checkoutSource).toContain("PhysicalCommercePaused");
    expect(checkoutSource).toContain("Checkout");
    expect(checkoutSource).not.toContain("getOrderQuote");
  });

  it("handles product shipping loading and network error states", () => {
    expect(productSource).toContain('type ShippingState = "loading" | "ready" | "error"');
    expect(productSource).toContain("Shipping could not be checked right now");
    expect(productSource).toContain('aria-live="polite"');
  });

  it("uses resilient product and cart image fallbacks", () => {
    expect(productSource).toContain("PLACEHOLDER_IMAGE");
    expect(productSource).toContain("onError={() => markImageFailed");
    expect(cartSource).toContain("PLACEHOLDER_IMAGE");
    expect(cardSource).toContain("onError={() => setImageFailed(true)}");
  });

  it("prevents rapid duplicate product actions and invalid quantities", () => {
    expect(productSource).toContain("actionLocked");
    expect(productSource).toContain("disabled={quantity <= 1}");
    expect(productSource).toContain("Math.min(maxQuantity");
  });

  it("shows cart loading and catalog error states", () => {
    expect(cartSource).toContain("Loading your cart");
    expect(cartSource).toContain("catalogError");
    expect(cartSource).toContain('role="alert"');
  });

  it("does not reintroduce disallowed checkout behavior", () => {
    expect(checkoutSource).not.toContain("NEXT_PUBLIC_PRICING_FX_RATE");
    expect(checkoutSource).not.toContain("INR_PER_USD");
    expect(checkoutSource).not.toContain("Stripe");
    expect(checkoutSource).not.toContain("Razorpay");
  });
});
