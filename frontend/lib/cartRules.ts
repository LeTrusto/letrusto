import type { CartItem, CommerceProduct } from "@/types/commerce";

export type CartCatalog = Record<string, Pick<CommerceProduct, "price" | "catalogVariants" | "madeToOrder">>;

function variantFor(catalog: CartCatalog, item: CartItem) {
  return catalog[item.productId]?.catalogVariants?.find((variant) => variant.id === item.selectedVariantId);
}

function variantInventory(catalog: CartCatalog, item: CartItem): number | null {
  const product = catalog[item.productId];
  if (!product) return null;
  const variant = variantFor(catalog, item);
  if (!variant) return product.catalogVariants?.length ? 0 : Number.MAX_SAFE_INTEGER;
  if (!variant.available) return 0;
  if (product.madeToOrder) return Number.MAX_SAFE_INTEGER;
  return Math.max(0, variant.inventory);
}

export function normalizeCartItems(items: CartItem[], catalog: CartCatalog): CartItem[] {
  const normalized: CartItem[] = [];
  for (const item of items) {
    if (!item.productId || item.quantity < 1) continue;
    const inventory = variantInventory(catalog, item);
    if (inventory === null || inventory <= 0) continue;
    const quantity = Math.min(Math.floor(item.quantity), inventory);
    const existing = normalized.find((candidate) => candidate.productId === item.productId && candidate.selectedVariantId === item.selectedVariantId);
    if (existing) {
      existing.quantity = Math.min(existing.quantity + quantity, inventory);
    } else {
      normalized.push({ ...item, quantity });
    }
  }
  return normalized;
}

export function cartItemsEqual(first: CartItem[], second: CartItem[]): boolean {
  if (first.length !== second.length) return false;
  return first.every((item, index) => {
    const other = second[index];
    return item.productId === other.productId && item.selectedVariantId === other.selectedVariantId && item.quantity === other.quantity;
  });
}

export function addCartItem(items: CartItem[], catalog: CartCatalog, productId: string, quantity = 1, selectedVariantId?: string): CartItem[] {
  if (quantity < 1) return items;
  const item = { productId, quantity: Math.floor(quantity), selectedVariantId };
  const inventory = variantInventory(catalog, item);
  if (inventory !== null && inventory <= 0) return items;
  const maxQuantity = inventory ?? Number.MAX_SAFE_INTEGER;
  const existing = items.find((candidate) => candidate.productId === productId && candidate.selectedVariantId === selectedVariantId);
  if (existing) {
    const nextQuantity = Math.min(existing.quantity + item.quantity, maxQuantity);
    if (nextQuantity === existing.quantity) return items;
    return items.map((candidate) => candidate === existing ? { ...candidate, quantity: nextQuantity } : candidate);
  }
  return [...items, { ...item, quantity: Math.min(item.quantity, maxQuantity) }];
}

export function updateCartItemQuantity(items: CartItem[], catalog: CartCatalog, productId: string, quantity: number, selectedVariantId?: string): CartItem[] {
  if (quantity < 1) return items;
  const requestedQuantity = Math.floor(quantity);
  return items.map((item) => {
    if (item.productId !== productId || item.selectedVariantId !== selectedVariantId) return item;
    const inventory = variantInventory(catalog, item);
    if (inventory !== null && inventory <= 0) return item;
    return { ...item, quantity: Math.min(requestedQuantity, inventory ?? requestedQuantity) };
  });
}

export function cartSubtotal(items: CartItem[], catalog: CartCatalog): number {
  return items.reduce((sum, item) => {
    const product = catalog[item.productId];
    const variant = variantFor(catalog, item);
    return sum + (variant?.price ?? product?.price ?? 0) * item.quantity;
  }, 0);
}
