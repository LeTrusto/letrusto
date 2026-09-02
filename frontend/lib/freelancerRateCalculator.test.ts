import { describe, expect, it } from "vitest";
import { calculateFreelancerRate, validateFreelancerRateInputs } from "./freelancerRateCalculator";

describe("freelancer rate calculator", () => {
  it("accounts for expenses and unpaid time", () => expect(calculateFreelancerRate(60000, 10000, 80, 20)).toEqual({ monthlyTarget: 70000, hourlyRate: 1093.75, dailyRate: 8750 }));
  it("rejects zero billable hours", () => expect(validateFreelancerRateInputs(1, 1, 0, 20)).toContain("greater than zero"));
});
