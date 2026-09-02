import { describe, expect, it } from "vitest";
import { calculateCommission, validateCommissionInputs } from "./commissionCalculator";

describe("commission calculator", () => {
  it("calculates commission and net amount", () => expect(calculateCommission(10000, 12.5)).toEqual({ commission: 1250, netAmount: 8750 }));
  it("rejects invalid rates", () => expect(validateCommissionInputs(100, 101)).toContain("between"));
});
