import { describe, expect, it } from "vitest";
import { calculatePricing, validatePricingInputs } from "./pricingCalculator";

describe("calculatePricing", () => {
  it("calculates a selling price, profit, margin, and markup", () => {
    expect(calculatePricing(600, 25)).toMatchObject({ sellingPrice: 800, profit: 200, margin: 25, markup: 33.33333333333333 });
  });
  it("supports zero margin, zero cost, decimals, and large values", () => {
    expect(calculatePricing(500, 0)).toMatchObject({ sellingPrice: 500, profit: 0, margin: 0, markup: 0 });
    expect(calculatePricing(0, 40)).toMatchObject({ sellingPrice: 0, profit: 0, margin: null, markup: null });
    expect(calculatePricing(1250.5, 12.5).profit).toBeCloseTo(178.642857, 5);
    expect(calculatePricing(999999999, 50).sellingPrice).toBe(1999999998);
  });
  it("rejects invalid or 100% margins", () => {
    expect(validatePricingInputs(-1, 20)).toContain("zero or greater");
    expect(validatePricingInputs(100, -1)).toContain("zero or greater");
    expect(validatePricingInputs(100, 100)).toContain("below 100");
    expect(() => calculatePricing(100, 100)).toThrow();
  });
});
