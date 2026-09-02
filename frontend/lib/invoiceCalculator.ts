export type DiscountType = "percentage" | "fixed";

export type InvoiceItem = {
  id: string;
  description: string;
  quantity: number;
  unitPrice: number;
};

export type CalculatedInvoiceItem = InvoiceItem & { total: number };

export type InvoiceCalculation = {
  items: CalculatedInvoiceItem[];
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
};

export function validateInvoiceItem(item: Pick<InvoiceItem, "description" | "quantity" | "unitPrice">): string | null {
  if (!item.description.trim()) return "Add a description for this item.";
  if (!Number.isFinite(item.quantity) || item.quantity <= 0) return "Quantity must be greater than zero.";
  if (!Number.isFinite(item.unitPrice) || item.unitPrice < 0) return "Unit price must be zero or greater.";
  return null;
}

export function validateInvoiceItems(items: InvoiceItem[]): string | null {
  if (items.length === 0) return "Add at least one invoice item.";
  for (const item of items) {
    const error = validateInvoiceItem(item);
    if (error) return error;
  }
  return null;
}

export function calculateInvoice(
  items: InvoiceItem[],
  discountType: DiscountType,
  discountValue: number,
  taxRate: number,
): InvoiceCalculation {
  const itemError = validateInvoiceItems(items);
  if (itemError) throw new Error(itemError);
  if (!Number.isFinite(discountValue) || discountValue < 0) throw new Error("Discount must be zero or greater.");
  if (discountType === "percentage" && discountValue > 100) throw new Error("Percentage discount cannot exceed 100%.");
  if (!Number.isFinite(taxRate) || taxRate < 0 || taxRate > 100) throw new Error("Tax rate must be between 0% and 100%.");

  const calculatedItems = items.map((item) => ({ ...item, total: item.quantity * item.unitPrice }));
  if (calculatedItems.some((item) => !Number.isFinite(item.total))) throw new Error("Item values are too large to calculate.");
  const subtotal = calculatedItems.reduce((sum, item) => sum + item.total, 0);
  if (!Number.isFinite(subtotal)) throw new Error("Item values are too large to calculate.");
  const discount = discountType === "percentage" ? subtotal * (discountValue / 100) : discountValue;
  if (discount > subtotal) throw new Error("Discount cannot be greater than the subtotal.");
  const taxableAmount = subtotal - discount;
  const tax = taxableAmount * (taxRate / 100);
  if (!Number.isFinite(tax) || !Number.isFinite(taxableAmount) || !Number.isFinite(taxableAmount + tax)) throw new Error("Invoice values are too large to calculate.");

  return {
    items: calculatedItems,
    subtotal,
    discount,
    tax,
    total: taxableAmount + tax,
  };
}
