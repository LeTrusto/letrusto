import { describe, expect, it } from "vitest";
import { calculateProfitMargin, validateAmount } from "./profitMarginCalculator";

describe("calculateProfitMargin", () => {
  it("calculates profit, margin, and markup", () => {
    expect(calculateProfitMargin(60, 100)).toEqual({
      profit: 40,
      margin: 40,
      markup: 66.66666666666666,
      status: "profit",
    });
  });

  it("identifies break-even", () => {
    expect(calculateProfitMargin(100, 100)).toEqual({ profit: 0, margin: 0, markup: 0, status: "break-even" });
  });

  it("identifies loss", () => {
    expect(calculateProfitMargin(120, 100)).toEqual({ profit: -20, margin: -20, markup: -16.666666666666664, status: "loss" });
  });

  it("supports decimal values and large reasonable values", () => {
    const calculation = calculateProfitMargin(1250.5, 1999.99);
    expect(calculation.profit).toBeCloseTo(749.49, 2);
    expect(calculation.margin).toBeCloseTo(37.4746873734, 10);
    expect(calculation.markup).toBeCloseTo(59.9352259096, 10);
    expect(calculation.status).toBe("profit");
    expect(calculateProfitMargin(999999999.99, 1299999999.99).status).toBe("profit");
  });

  it("avoids division by zero when cost or selling price is zero", () => {
    expect(calculateProfitMargin(0, 100)).toEqual({ profit: 100, margin: 100, markup: null, status: "profit" });
    expect(calculateProfitMargin(100, 0)).toEqual({ profit: -100, margin: null, markup: -100, status: "loss" });
    expect(calculateProfitMargin(0, 0)).toEqual({ profit: 0, margin: null, markup: null, status: "break-even" });
  });

  it("rejects negative and non-finite amounts", () => {
    expect(() => calculateProfitMargin(-1, 100)).toThrow();
    expect(() => calculateProfitMargin(100, Number.NaN)).toThrow();
  });
});

describe("validateAmount", () => {
  it("handles empty, invalid, negative, and valid values", () => {
    expect(validateAmount("", "Cost price")).toBe("Cost price is required.");
    expect(validateAmount("abc", "Cost price")).toBe("Cost price must be a valid number.");
    expect(validateAmount("-1", "Cost price")).toBe("Cost price cannot be negative.");
    expect(validateAmount("125.50", "Cost price")).toBeNull();
  });
});
