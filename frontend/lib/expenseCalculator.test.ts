import { describe, expect, it } from "vitest";
import { calculateExpenses, validateExpense, type ExpenseEntry } from "./expenseCalculator";

const expense = (overrides: Partial<ExpenseEntry> = {}): ExpenseEntry => ({ id: "1", name: "Hosting", category: "Software", amount: 500, ...overrides });

describe("calculateExpenses", () => {
  it("calculates one and multiple expenses with category totals", () => {
    expect(calculateExpenses([expense()])).toEqual({ total: 500, count: 1, categoryTotals: { Software: 500 } });
    expect(calculateExpenses([expense(), expense({ id: "2", name: "Rent", category: "Rent", amount: 1000 }), expense({ id: "3", name: "Domain", amount: 250.5 })])).toEqual({ total: 1750.5, count: 3, categoryTotals: { Software: 750.5, Rent: 1000 } });
  });
  it("supports zero, decimals, and large values", () => {
    expect(calculateExpenses([expense({ amount: 0 })]).total).toBe(0);
    expect(calculateExpenses([expense({ amount: 999999999 })]).total).toBe(999999999);
  });
  it("rejects invalid and negative entries", () => {
    expect(validateExpense(expense({ name: "" }))).toContain("required");
    expect(validateExpense(expense({ category: "" }))).toContain("category");
    expect(validateExpense(expense({ amount: -1 }))).toContain("zero or greater");
    expect(() => calculateExpenses([expense({ amount: -1 })])).toThrow();
  });
});
