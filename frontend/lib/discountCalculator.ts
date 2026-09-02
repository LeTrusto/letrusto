export type DiscountCalculation = { savings: number; finalPrice: number };

export function validateDiscountInputs(price: number, rate: number) {
  if (!Number.isFinite(price) || price <= 0) return "Original price must be greater than zero.";
  if (!Number.isFinite(rate) || rate < 0 || rate > 100) return "Discount must be between 0% and 100%.";
  return null;
}

export function calculateDiscount(price: number, rate: number): DiscountCalculation {
  const error = validateDiscountInputs(price, rate);
  if (error) throw new Error(error);
  const savings = price * rate / 100;
  return { savings, finalPrice: price - savings };
}
