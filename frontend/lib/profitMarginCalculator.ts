export type CalculationStatus = "profit" | "break-even" | "loss";

export type ProfitMarginCalculation = {
  profit: number;
  margin: number | null;
  markup: number | null;
  status: CalculationStatus;
};

export function validateAmount(value: string, label: string): string | null {
  if (value.trim() === "") return `${label} is required.`;

  const amount = Number(value);
  if (!Number.isFinite(amount)) return `${label} must be a valid number.`;
  if (amount < 0) return `${label} cannot be negative.`;

  return null;
}

export function calculateProfitMargin(cost: number, sellingPrice: number): ProfitMarginCalculation {
  if (!Number.isFinite(cost) || !Number.isFinite(sellingPrice) || cost < 0 || sellingPrice < 0) {
    throw new Error("Cost and selling price must be finite, non-negative numbers.");
  }

  const profit = sellingPrice - cost;

  return {
    profit,
    margin: sellingPrice === 0 ? null : (profit / sellingPrice) * 100,
    markup: cost === 0 ? null : (profit / cost) * 100,
    status: profit > 0 ? "profit" : profit < 0 ? "loss" : "break-even",
  };
}
