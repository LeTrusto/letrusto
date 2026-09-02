import { describe, expect, it } from "vitest";
import { calculateInvoice, validateInvoiceItem, validateInvoiceItems, type InvoiceItem } from "./invoiceCalculator";

const item = (overrides: Partial<InvoiceItem> = {}): InvoiceItem => ({ id: "1", description: "Website setup", quantity: 2, unitPrice: 500, ...overrides });

describe("calculateInvoice", () => {
  it("calculates one line item", () => {
    expect(calculateInvoice([item()], "fixed", 0, 0)).toMatchObject({ subtotal: 1000, discount: 0, tax: 0, total: 1000 });
  });

  it("calculates multiple items with decimal quantities and prices", () => {
    const result = calculateInvoice([item(), item({ id: "2", description: "Support", quantity: 1.5, unitPrice: 250.75 })], "fixed", 0, 0);
    expect(result.items.map(({ total }) => total)).toEqual([1000, 376.125]);
    expect(result.subtotal).toBeCloseTo(1376.125, 3);
  });

  it("applies percentage and fixed discounts", () => {
    expect(calculateInvoice([item()], "percentage", 10, 0)).toMatchObject({ discount: 100, total: 900 });
    expect(calculateInvoice([item()], "fixed", 125, 0)).toMatchObject({ discount: 125, total: 875 });
  });

  it("applies tax after discount", () => {
    expect(calculateInvoice([item()], "fixed", 100, 18)).toMatchObject({ subtotal: 1000, discount: 100, tax: 162, total: 1062 });
  });

  it("supports zero values and large values", () => {
    expect(calculateInvoice([item({ quantity: 1, unitPrice: 0 })], "fixed", 0, 0).total).toBe(0);
    expect(calculateInvoice([item({ quantity: 1000000, unitPrice: 999999 })], "fixed", 0, 0).total).toBe(999999000000);
    expect(() => calculateInvoice([item({ quantity: Number.MAX_VALUE, unitPrice: 2 })], "fixed", 0, 0)).toThrow("too large");
  });

  it("rejects invalid discounts, tax, and empty items", () => {
    expect(() => calculateInvoice([], "fixed", 0, 0)).toThrow("at least one");
    expect(() => calculateInvoice([item()], "fixed", 1001, 0)).toThrow("greater than the subtotal");
    expect(() => calculateInvoice([item()], "percentage", 101, 0)).toThrow("100%");
    expect(() => calculateInvoice([item()], "fixed", 0, -1)).toThrow("between 0%");
  });
});

describe("invoice item validation", () => {
  it("rejects missing descriptions and invalid quantities or prices", () => {
    expect(validateInvoiceItem(item({ description: "" }))).toContain("description");
    expect(validateInvoiceItem(item({ quantity: 0 }))).toContain("greater than zero");
    expect(validateInvoiceItem(item({ quantity: -1 }))).toContain("greater than zero");
    expect(validateInvoiceItem(item({ unitPrice: -1 }))).toContain("zero or greater");
    expect(validateInvoiceItems([])).toContain("at least one");
  });
});
