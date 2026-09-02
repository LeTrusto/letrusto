export type CommissionCalculation = { commission: number; netAmount: number };

export function validateCommissionInputs(amount: number, rate: number) {
  if (!Number.isFinite(amount) || amount < 0) return "Amount must be zero or greater.";
  if (!Number.isFinite(rate) || rate < 0 || rate > 100) return "Commission rate must be between 0% and 100%.";
  return null;
}

export function calculateCommission(amount: number, rate: number): CommissionCalculation {
  const error = validateCommissionInputs(amount, rate);
  if (error) throw new Error(error);
  const commission = amount * rate / 100;
  return { commission, netAmount: amount - commission };
}
