import { describe, expect, it } from "vitest";
import { calculateBreakEven, validateBreakEvenInputs } from "./breakEvenCalculator";

describe("calculateBreakEven", () => {
  it("calculates contribution, quantity, and revenue", () => {
    const result = calculateBreakEven(1000, 20, 50);
    expect(result.contributionPerUnit).toBe(30);
    expect(result.breakEvenQuantity).toBeCloseTo(33.3333333333, 10);
    expect(result.breakEvenUnits).toBe(34);
    expect(result.breakEvenRevenue).toBeCloseTo(1666.6666666667, 10);
  });
  it("supports decimal values, zero fixed costs, and large values", () => {
    expect(calculateBreakEven(0, 12.5, 25)).toMatchObject({ contributionPerUnit: 12.5, breakEvenQuantity: 0, breakEvenUnits: 0, breakEvenRevenue: 0 });
    expect(calculateBreakEven(1250.5, 10.25, 30).breakEvenUnits).toBe(64);
    expect(calculateBreakEven(999999999, 1, 2).breakEvenRevenue).toBe(1999999998);
  });
  it("rejects zero or negative contribution", () => {
    expect(validateBreakEvenInputs(100, 50, 50)).toContain("greater than variable");
    expect(validateBreakEvenInputs(100, 60, 50)).toContain("greater than variable");
    expect(() => calculateBreakEven(100, 50, 50)).toThrow();
    expect(() => calculateBreakEven(-1, 10, 20)).toThrow();
  });
});
