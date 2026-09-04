import { describe, expect, it } from "vitest";
import { DIGITAL_PRODUCT_CATEGORIES, DIGITAL_PRODUCTS, formatDigitalProductPrice, getDigitalProductBySlug, getPublishedDigitalProducts } from "./digitalProducts";

describe("digital product catalog", () => {
  it("publishes only products with a published status", () => {
    expect(getPublishedDigitalProducts()).toEqual(DIGITAL_PRODUCTS.filter((product) => product.status === "published"));
    expect(getPublishedDigitalProducts()[0].delivery).toBe("protected-download");
  });

  it("resolves a published product by slug and rejects missing products", () => {
    expect(getDigitalProductBySlug("small-business-finance-pricing-toolkit")?.name).toBe("Small Business Finance & Pricing Kit");
    expect(getDigitalProductBySlug("does-not-exist")).toBeUndefined();
  });

  it("keeps categories reusable and prices configurable", () => {
    expect(DIGITAL_PRODUCT_CATEGORIES.map((category) => category.slug)).toContain("business");
    expect(formatDigitalProductPrice({ price: 199, currency: "INR" })).toBe("₹199");
  });
});