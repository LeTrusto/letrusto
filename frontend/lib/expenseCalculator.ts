export type ExpenseEntry = {
  id: string;
  name: string;
  category: string;
  amount: number;
};

export type ExpenseCalculation = {
  total: number;
  count: number;
  categoryTotals: Record<string, number>;
};

export function validateExpense(entry: Pick<ExpenseEntry, "name" | "category" | "amount">): string | null {
  if (!entry.name.trim()) return "Expense name is required.";
  if (!entry.category.trim()) return "Choose an expense category.";
  if (!Number.isFinite(entry.amount) || entry.amount < 0) return "Amount must be zero or greater.";
  return null;
}

export function calculateExpenses(entries: ExpenseEntry[]): ExpenseCalculation {
  for (const entry of entries) {
    const error = validateExpense(entry);
    if (error) throw new Error(error);
  }

  const categoryTotals: Record<string, number> = {};
  let total = 0;
  for (const entry of entries) {
    total += entry.amount;
    categoryTotals[entry.category] = (categoryTotals[entry.category] ?? 0) + entry.amount;
  }
  if (!Number.isFinite(total) || Object.values(categoryTotals).some((value) => !Number.isFinite(value))) throw new Error("Expense values are too large to calculate.");
  return { total, count: entries.length, categoryTotals };
}
