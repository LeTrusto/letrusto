"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { usePathname } from "next/navigation";
import type { CartItem } from "@/types/commerce";
import { addCartItem, cartItemsEqual, cartSubtotal, normalizeCartItems, updateCartItemQuantity } from "@/lib/cartRules";
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
  cartReady: boolean;
  catalogReady: boolean;
  catalogError: string;
};

const CartContext = createContext<CartContextValue | null>(null);

function saveCart(items: CartItem[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch { /* quota exceeded — silent */ }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const shouldLoadCatalog = ["/cart", "/checkout", "/product", "/products", "/shop"].some((route) => pathname === route || pathname.startsWith(`${route}/`));
  const [items, setItems] = useState<CartItem[]>([]);
  const [hydrated, setHydrated] = useState(false);
  const [products, setProducts] = useState<Record<string, ReturnType<typeof toCommerceProduct>>>({});
  const [catalogReady, setCatalogReady] = useState(false);
  const [catalogError, setCatalogError] = useState("");

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
    if (!shouldLoadCatalog) return;
    void getPublicProducts().then((catalog) => {
      const nextProducts = Object.fromEntries(catalog.map((product) => {
        const commerceProduct = toCommerceProduct(product);
        return [commerceProduct.id, commerceProduct];
      }));
      setProducts(nextProducts);
      setItems((current) => normalizeCartItems(current, nextProducts));
      setCatalogReady(true);
      setCatalogError("");
    }).catch(() => {
      setCatalogReady(false);
      setCatalogError("Unable to load current product details. Please refresh and try again.");
    });
  }, [shouldLoadCatalog]);

  useEffect(() => {
    if (!hydrated) return;
    saveCart(items);
  }, [hydrated, items]);

  useEffect(() => {
    if (!hydrated || !catalogReady) return;
    void Promise.resolve().then(() => {
      setItems((current) => {
        const normalized = normalizeCartItems(current, products);
        return cartItemsEqual(current, normalized) ? current : normalized;
      });
    });
  }, [catalogReady, hydrated, products]);

  const addItem = useCallback((productId: string, quantity = 1, selectedVariantId?: string) => {
    setItems((prev) => addCartItem(prev, products, productId, quantity, selectedVariantId));
  }, [products]);

  const removeItem = useCallback((productId: string, selectedVariantId?: string) => {
    setItems((prev) => prev.filter((item) => item.productId !== productId || item.selectedVariantId !== selectedVariantId));
  }, []);

  const updateQuantity = useCallback((productId: string, quantity: number, selectedVariantId?: string) => {
    setItems((prev) => updateCartItemQuantity(prev, products, productId, quantity, selectedVariantId));
  }, [products]);

  const clearCart = useCallback(() => setItems([]), []);

  const itemCount = items.reduce((sum, i) => sum + i.quantity, 0);

  const subtotal = cartSubtotal(items, products);

  const savings = 0;

  return (
    <CartContext.Provider
      value={{ items, addItem, removeItem, updateQuantity, clearCart, itemCount, subtotal, savings, cartReady: hydrated, catalogReady, catalogError }}
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
