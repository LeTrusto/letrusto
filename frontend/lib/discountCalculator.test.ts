import { describe, expect, it } from "vitest";
import { calculateDiscount, validateDiscountInputs } from "./discountCalculator";

describe("discount calculator", () => {
  it("calculates savings and final price", () => expect(calculateDiscount(799, 15)).toEqual({ savings: 119.85, finalPrice: 679.15 }));
  it("rejects zero prices", () => expect(validateDiscountInputs(0, 10)).toContain("greater than zero"));
});
