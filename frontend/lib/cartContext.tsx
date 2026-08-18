"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import type { CartItem } from "@/types/commerce";
import { getPublicProducts, toCommerceProduct } from "@/services/product.service";

const STORAGE_KEY = "letrusto:cart";

type CartContextValue = {
  items: CartItem[];
  addItem: (productId: string, quantity?: number, selectedVariantId?: string) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
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
  const [items, setItems] = useState<CartItem[]>(() => {
    if (typeof window === "undefined") return [];
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? (JSON.parse(raw) as CartItem[]) : [];
    } catch {
      return [];
    }
  });
  const [products, setProducts] = useState<Record<string, ReturnType<typeof toCommerceProduct>>>({});

  useEffect(() => {
    void getPublicProducts().then((catalog) => {
      setProducts(Object.fromEntries(catalog.map((product) => {
        const commerceProduct = toCommerceProduct(product);
        return [commerceProduct.id, commerceProduct];
      })));
    }).catch(() => {});
  }, []);

  useEffect(() => {
    saveCart(items);
  }, [items]);

  const addItem = useCallback((productId: string, quantity = 1, selectedVariantId?: string) => {
    setItems((prev) => {
      const existing = prev.find((i) => i.productId === productId && i.selectedVariantId === selectedVariantId);
      if (existing) {
        return prev.map((i) =>
          i === existing ? { ...i, quantity: i.quantity + quantity } : i
        );
      }
      return [...prev, { productId, quantity, selectedVariantId }];
    });
  }, []);

  const removeItem = useCallback((productId: string) => {
    setItems((prev) => prev.filter((i) => i.productId !== productId));
  }, []);

  const updateQuantity = useCallback((productId: string, quantity: number) => {
    if (quantity <= 0) {
      setItems((prev) => prev.filter((i) => i.productId !== productId));
      return;
    }
    setItems((prev) =>
      prev.map((i) => (i.productId === productId ? { ...i, quantity } : i))
    );
  }, []);

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
