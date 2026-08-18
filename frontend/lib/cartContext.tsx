"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import type { CartItem } from "@/types/commerce";
import { getPublicProducts, toCommerceProduct } from "@/services/product.service";

const STORAGE_KEY = "letrusto:cart";

type CartContextValue = {
  items: CartItem[];
  addItem: (productId: string, quantity?: number, selectedVariantId?: string) => void;
  removeItem: (productId: string, selectedVariantId?: string) => void;
  updateQuantity: (productId: string, quantity: number, selectedVariantId?: string) => void;
  clearCart: () => void;
  itemCount: number;
  subtotal: number;
  savings: number;
};

const CartContext = createContext<CartContextValue | null>(null);

function saveCart(items: CartItem[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch { /* quota exceeded — silent */ }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [hydrated, setHydrated] = useState(false);
  const [products, setProducts] = useState<Record<string, ReturnType<typeof toCommerceProduct>>>({});

  useEffect(() => {
    void Promise.resolve().then(() => {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) setItems(JSON.parse(raw) as CartItem[]);
      } catch { /* ignore malformed local cart */ }
      setHydrated(true);
    });
  }, []);

  useEffect(() => {
    void getPublicProducts().then((catalog) => {
      setProducts(Object.fromEntries(catalog.map((product) => {
        const commerceProduct = toCommerceProduct(product);
        return [commerceProduct.id, commerceProduct];
      })));
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    saveCart(items);
  }, [hydrated, items]);

  const addItem = useCallback((productId: string, quantity = 1, selectedVariantId?: string) => {
    const product = products[productId];
    const variant = product?.catalogVariants?.find((candidate) => candidate.id === selectedVariantId);
    if (variant && (!variant.available || quantity > variant.inventory)) return;
    setItems((prev) => {
      const existing = prev.find((i) => i.productId === productId && i.selectedVariantId === selectedVariantId);
      const nextQuantity = quantity + (existing?.quantity ?? 0);
      if (variant && nextQuantity > variant.inventory) return prev;
      if (existing) {
        return prev.map((i) =>
          i === existing ? { ...i, quantity: i.quantity + quantity } : i
        );
      }
      return [...prev, { productId, quantity, selectedVariantId }];
    });
  }, [products]);

  const removeItem = useCallback((productId: string, selectedVariantId?: string) => {
    setItems((prev) => prev.filter((item) => item.productId !== productId || item.selectedVariantId !== selectedVariantId));
  }, []);

  const updateQuantity = useCallback((productId: string, quantity: number, selectedVariantId?: string) => {
    if (quantity <= 0) {
      setItems((prev) => prev.filter((item) => item.productId !== productId || item.selectedVariantId !== selectedVariantId));
      return;
    }
    setItems((prev) => prev.map((item) => {
      if (item.productId !== productId || item.selectedVariantId !== selectedVariantId) return item;
      const inventory = products[item.productId]?.catalogVariants?.find((variant) => variant.id === item.selectedVariantId)?.inventory;
      return inventory !== undefined && quantity > inventory ? item : { ...item, quantity };
    }));
  }, [products]);

  const clearCart = useCallback(() => setItems([]), []);

  const itemCount = items.reduce((sum, i) => sum + i.quantity, 0);

  const subtotal = items.reduce((sum, item) => {
    const product = products[item.productId];
    const variant = product?.catalogVariants?.find((candidate) => candidate.id === item.selectedVariantId);
    return sum + (variant?.price ?? product?.price ?? 0) * item.quantity;
  }, 0);

  const savings = 0;

  return (
    <CartContext.Provider
      value={{ items, addItem, removeItem, updateQuantity, clearCart, itemCount, subtotal, savings }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
