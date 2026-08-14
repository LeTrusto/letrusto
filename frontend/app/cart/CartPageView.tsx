"use client";

import Image from "next/image";
import Link from "next/link";
import { Minus, Plus, Trash2, ShoppingBag } from "lucide-react";
import { useCart } from "@/lib/cartContext";
import { getMockProductById } from "@/lib/mockData";

function formatPrice(value: number): string {
  return `₹${value.toLocaleString("en-IN")}`;
}

export default function CartPageView() {
  const { items, updateQuantity, removeItem, clearCart, subtotal, savings, itemCount } = useCart();

  if (items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <ShoppingBag size={48} strokeWidth={1} className="mx-auto text-[var(--text-muted)]" />
        <h1 className="mt-4 text-xl font-bold text-[var(--text-primary)]">Your cart is empty</h1>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">Looks like you haven&apos;t added anything yet.</p>
        <Link href="/shop" className="lt-btn lt-btn-lg lt-btn-primary mt-6 inline-flex">
          Start Shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-6 py-6 md:py-10">
      <div className="flex items-center justify-between mb-6">
        <h1 className="lt-heading-2">Cart ({itemCount})</h1>
        <button onClick={clearCart} className="text-sm text-[var(--text-muted)] hover:text-[var(--lt-rose)] transition-colors">
          Clear Cart
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Items */}
        <div className="md:col-span-2 space-y-4">
          {items.map((item) => {
            const product = getMockProductById(item.productId);
            if (!product) return null;

            return (
              <div key={item.productId} className="lt-card p-4 flex gap-4">
                <Link href={`/product/${product.slug}`} className="shrink-0">
                  <div className="relative w-20 h-20 md:w-24 md:h-24 rounded-lg overflow-hidden bg-[var(--surface-muted)]">
                    <Image
                      src={product.images[0] ?? "/images/products/placeholder.svg"}
                      alt={product.name}
                      fill
                      sizes="96px"
                      className="object-cover"
                    />
                  </div>
                </Link>
                <div className="flex-1 min-w-0">
                  <Link href={`/product/${product.slug}`} className="text-sm font-semibold text-[var(--text-primary)] line-clamp-2 hover:underline">
                    {product.name}
                  </Link>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">{product.categoryLabel}</p>
                  <div className="mt-2 flex items-center gap-1.5">
                    <span className="text-sm font-bold">{formatPrice(product.price)}</span>
                    {product.compareAtPrice && (
                      <span className="text-xs text-[var(--text-muted)] line-through">{formatPrice(product.compareAtPrice)}</span>
                    )}
                  </div>
                  <div className="mt-3 flex items-center justify-between">
                    <div className="flex items-center border border-[var(--border)] rounded-md">
                      <button
                        onClick={() => updateQuantity(item.productId, item.quantity - 1)}
                        className="w-8 h-8 flex items-center justify-center hover:bg-[var(--surface-muted)] transition-colors"
                        aria-label="Decrease quantity"
                      >
                        <Minus size={14} />
                      </button>
                      <span className="w-8 h-8 flex items-center justify-center text-sm font-semibold border-x border-[var(--border)]">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => updateQuantity(item.productId, item.quantity + 1)}
                        className="w-8 h-8 flex items-center justify-center hover:bg-[var(--surface-muted)] transition-colors"
                        aria-label="Increase quantity"
                      >
                        <Plus size={14} />
                      </button>
                    </div>
                    <button
                      onClick={() => removeItem(item.productId)}
                      className="p-1.5 text-[var(--text-muted)] hover:text-[var(--lt-rose)] transition-colors"
                      aria-label={`Remove ${product.name}`}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Summary */}
        <div className="md:col-span-1">
          <div className="lt-card p-5 sticky top-20">
            <h2 className="text-sm font-bold text-[var(--text-primary)] mb-4">Order Summary</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-[var(--text-secondary)]">Subtotal</span>
                <span className="font-semibold">{formatPrice(subtotal)}</span>
              </div>
              {savings > 0 && (
                <div className="flex justify-between text-[var(--lt-success)]">
                  <span>You Save</span>
                  <span className="font-semibold">−{formatPrice(savings)}</span>
                </div>
              )}
              <div className="flex justify-between text-[var(--text-muted)]">
                <span>Shipping</span>
                <span>Calculated at checkout</span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-[var(--border)] flex justify-between text-base font-bold">
              <span>Total</span>
              <span>{formatPrice(subtotal)}</span>
            </div>
            <button className="lt-btn lt-btn-lg lt-btn-primary w-full mt-5" disabled>
              Proceed to Checkout
            </button>
            <p className="text-[10px] text-[var(--text-muted)] text-center mt-2">
              Checkout coming soon — development preview only
            </p>
            <Link href="/shop" className="lt-btn lt-btn-md lt-btn-ghost w-full mt-2">
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
