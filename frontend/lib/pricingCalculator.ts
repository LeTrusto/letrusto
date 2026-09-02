export type PricingCalculation = {
  sellingPrice: number;
  profit: number;
  margin: number | null;
  markup: number | null;
};

export function validatePricingInputs(cost: number, margin: number): string | null {
  if (!Number.isFinite(cost) || cost < 0) return "Cost must be zero or greater.";
  if (!Number.isFinite(margin) || margin < 0) return "Profit margin must be zero or greater.";
  if (margin >= 100) return "Profit margin must be below 100%.";
  return null;
}

export function calculatePricing(cost: number, margin: number): PricingCalculation {
  const error = validatePricingInputs(cost, margin);
  if (error) throw new Error(error);

  const sellingPrice = cost / (1 - margin / 100);
  const profit = sellingPrice - cost;
  if (!Number.isFinite(sellingPrice) || !Number.isFinite(profit)) throw new Error("Values are too large to calculate.");

  return {
    sellingPrice,
    profit,
    margin: sellingPrice === 0 ? null : (profit / sellingPrice) * 100,
    markup: cost === 0 ? null : (profit / cost) * 100,
  };
}
