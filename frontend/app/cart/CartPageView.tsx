"use client";

import Image from "next/image";
import Link from "next/link";
import { Minus, Plus, Trash2, ShoppingBag } from "lucide-react";
import { useEffect, useState } from "react";
import { useCart } from "@/lib/cartContext";
import { getPublicProducts, toCommerceProduct } from "@/services/product.service";

function formatPrice(value: number): string {
  return `₹${value.toLocaleString("en-IN")}`;
}

export default function CartPageView() {
  const { items, updateQuantity, removeItem, clearCart, subtotal, savings, itemCount } = useCart();
  const [products, setProducts] = useState<Record<string, ReturnType<typeof toCommerceProduct>>>({});

  useEffect(() => {
    void getPublicProducts().then((catalog) => {
      setProducts(Object.fromEntries(catalog.map((product) => {
        const commerceProduct = toCommerceProduct(product);
        return [commerceProduct.id, commerceProduct];
      })));
    }).catch(() => {});
  }, []);

  if (items.length === 0) {
    return (
      <main className="mx-auto max-w-2xl px-4 py-20 text-center">
        <ShoppingBag size={48} strokeWidth={1} className="mx-auto text-[var(--text-muted)]" />
        <h1 className="mt-4 text-xl font-bold text-[var(--text-primary)]">Your cart is empty</h1>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">Looks like you haven&apos;t added anything yet.</p>
        <Link href="/shop" className="lt-btn lt-btn-lg lt-btn-primary mt-6 inline-flex">
          Start Shopping
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-6 md:px-6 md:py-10">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div><p className="lt-label">Your selection</p><h1 className="lt-heading-2 mt-1">Cart ({itemCount})</h1></div>
        <button type="button" onClick={clearCart} className="lt-btn lt-btn-ghost lt-btn-sm text-[var(--lt-rose)]" aria-label="Remove all items from cart">
          Clear Cart
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Items */}
        <div className="md:col-span-2 space-y-4">
          {items.map((item) => {
            const product = products[item.productId];
            if (!product) return null;
            const selectedVariant = product.catalogVariants?.find((variant) => variant.id === item.selectedVariantId);

            return (
              <div key={`${item.productId}-${item.selectedVariantId ?? "default"}`} className="lt-card flex gap-3 p-4 sm:gap-4">
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
                  {selectedVariant && <p className="text-xs text-[var(--text-secondary)] mt-1">Variant: {selectedVariant.label}</p>}
                  <div className="mt-2 flex items-center gap-1.5">
                    <span className="text-sm font-bold">{formatPrice(selectedVariant?.price ?? product.price)}</span>
                    {product.compareAtPrice && (
                      <span className="text-xs text-[var(--text-muted)] line-through">{formatPrice(product.compareAtPrice)}</span>
                    )}
                  </div>
                  <div className="mt-3 flex items-center justify-between gap-3">
                    <div className="flex items-center rounded-md border border-[var(--border)]" aria-label={`Quantity for ${product.name}${selectedVariant ? `, ${selectedVariant.label}` : ""}`}>
                      <button
                        type="button"
                        onClick={() => updateQuantity(item.productId, item.quantity - 1, item.selectedVariantId)}
                        className="w-8 h-8 flex items-center justify-center hover:bg-[var(--surface-muted)] transition-colors"
                        aria-label={`Decrease quantity for ${product.name}`}
                      >
                        <Minus size={14} />
                      </button>
                      <span className="w-8 h-8 flex items-center justify-center text-sm font-semibold border-x border-[var(--border)]">
                        {item.quantity}
                      </span>
                      <button
                        type="button"
                        onClick={() => updateQuantity(item.productId, item.quantity + 1, item.selectedVariantId)}
                        disabled={selectedVariant ? item.quantity >= selectedVariant.inventory : false}
                        className="w-8 h-8 flex items-center justify-center hover:bg-[var(--surface-muted)] transition-colors"
                        aria-label={`Increase quantity for ${product.name}`}
                      >
                        <Plus size={14} />
                      </button>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeItem(item.productId, item.selectedVariantId)}
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
          <div className="lt-card p-5 md:sticky md:top-20">
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
              <span>Subtotal</span>
              <span>{formatPrice(subtotal)}</span>
            </div>
            <p className="mt-2 text-xs text-[var(--text-muted)]">Shipping is charged separately and is added to your total at checkout.</p>
            <Link href="/checkout" className="lt-btn lt-btn-lg lt-btn-primary w-full mt-5 justify-center">
              Proceed to Checkout
            </Link>
            <p className="mt-3 text-center text-xs text-[var(--text-muted)]">
              You&apos;ll review payment after creating your order.
            </p>
            <Link href="/shop" className="lt-btn lt-btn-md lt-btn-ghost w-full mt-2">
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
