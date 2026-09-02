export type BreakEvenCalculation = {
  contributionPerUnit: number;
  breakEvenQuantity: number;
  breakEvenUnits: number;
  breakEvenRevenue: number;
};

export function validateBreakEvenInputs(fixedCosts: number, variableCost: number, sellingPrice: number): string | null {
  if (!Number.isFinite(fixedCosts) || fixedCosts < 0) return "Fixed costs must be zero or greater.";
  if (!Number.isFinite(variableCost) || variableCost < 0) return "Variable cost must be zero or greater.";
  if (!Number.isFinite(sellingPrice) || sellingPrice < 0) return "Selling price must be zero or greater.";
  if (sellingPrice <= variableCost) return "Selling price must be greater than variable cost to reach break-even.";
  return null;
}

export function calculateBreakEven(fixedCosts: number, variableCost: number, sellingPrice: number): BreakEvenCalculation {
  const error = validateBreakEvenInputs(fixedCosts, variableCost, sellingPrice);
  if (error) throw new Error(error);

  const contributionPerUnit = sellingPrice - variableCost;
  const breakEvenQuantity = fixedCosts / contributionPerUnit;
  const breakEvenUnits = Math.ceil(breakEvenQuantity);
  const breakEvenRevenue = breakEvenQuantity * sellingPrice;
  if (![contributionPerUnit, breakEvenQuantity, breakEvenUnits, breakEvenRevenue].every(Number.isFinite)) throw new Error("Values are too large to calculate.");

  return { contributionPerUnit, breakEvenQuantity, breakEvenUnits, breakEvenRevenue };
}
