export type FreelancerRateCalculation = { monthlyTarget: number; hourlyRate: number; dailyRate: number };

export function validateFreelancerRateInputs(monthlyIncome: number, monthlyExpenses: number, monthlyHours: number, buffer: number) {
  if (!Number.isFinite(monthlyIncome) || monthlyIncome < 0) return "Monthly income target must be zero or greater.";
  if (!Number.isFinite(monthlyExpenses) || monthlyExpenses < 0) return "Monthly expenses must be zero or greater.";
  if (!Number.isFinite(monthlyHours) || monthlyHours <= 0) return "Monthly billable hours must be greater than zero.";
  if (!Number.isFinite(buffer) || buffer < 0 || buffer >= 100) return "Unpaid-time buffer must be from 0% up to, but not including, 100%.";
  return null;
}

export function calculateFreelancerRate(monthlyIncome: number, monthlyExpenses: number, monthlyHours: number, buffer: number): FreelancerRateCalculation {
  const error = validateFreelancerRateInputs(monthlyIncome, monthlyExpenses, monthlyHours, buffer);
  if (error) throw new Error(error);
  const monthlyTarget = monthlyIncome + monthlyExpenses;
  const hourlyRate = monthlyTarget / (monthlyHours * (1 - buffer / 100));
  return { monthlyTarget, hourlyRate, dailyRate: hourlyRate * 8 };
}
