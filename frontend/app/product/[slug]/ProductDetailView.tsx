"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { Heart, Share2, ShoppingBag, Zap, Truck, RotateCcw, ChevronLeft } from "lucide-react";
import type { CommerceProduct } from "@/types/commerce";
import { useCart } from "@/lib/cartContext";
import CommerceProductCard from "@/components/products/CommerceProductCard";

function formatPrice(value: number): string {
  return `₹${value.toLocaleString("en-IN")}`;
}

type Props = {
  product: CommerceProduct;
  related: CommerceProduct[];
};

export default function ProductDetailView({ product, related }: Props) {
  const { addItem } = useCart();
  const [selectedVariants, setSelectedVariants] = useState<Record<string, string>>({});

  const discount = product.compareAtPrice
    ? Math.round(((product.compareAtPrice - product.price) / product.compareAtPrice) * 100)
    : 0;

  function handleShare() {
    if (typeof navigator !== "undefined" && navigator.share) {
      navigator.share({ title: product.name, url: window.location.href }).catch(() => {});
    }
  }

  return (
    <div className="bg-white min-h-screen">
      {/* Breadcrumb */}
      <div className="max-w-7xl mx-auto px-4 md:px-6 py-3">
        <Link href="/shop" className="inline-flex items-center gap-1 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
          <ChevronLeft size={14} />
          Back to Shop
        </Link>
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-6 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12">
          {/* Images */}
          <div className="relative aspect-square bg-[var(--surface-muted)] rounded-xl overflow-hidden">
            <Image
              src={product.images[0] ?? "/images/products/placeholder.svg"}
              alt={product.name}
              fill
              sizes="(max-width: 768px) 100vw, 50vw"
              className="object-cover"
              priority
            />
            {discount > 0 && (
              <span className="absolute top-3 left-3 lt-badge lt-badge-sale">{discount}% off</span>
            )}
          </div>

          {/* Details */}
          <div className="flex flex-col">
            <span className="lt-label text-[var(--text-muted)]">{product.categoryLabel}</span>
            <h1 className="mt-1 text-2xl md:text-3xl font-bold text-[var(--text-primary)] leading-tight">
              {product.name}
            </h1>

            {/* Price */}
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-[var(--text-primary)]">{formatPrice(product.price)}</span>
              {product.compareAtPrice && (
                <>
                  <span className="text-base text-[var(--text-muted)] line-through">{formatPrice(product.compareAtPrice)}</span>
                  <span className="text-sm font-semibold text-[var(--lt-rose)]">Save {formatPrice(product.compareAtPrice - product.price)}</span>
                </>
              )}
            </div>

            {/* Availability */}
            <div className="mt-3">
              {product.availability === "in-stock" && (
                <span className="text-sm font-medium text-[var(--lt-success)]">● In Stock</span>
              )}
              {product.availability === "limited" && (
                <span className="text-sm font-medium text-[var(--lt-accent-dark)]">● Limited Stock</span>
              )}
              {product.availability === "out-of-stock" && (
                <span className="text-sm font-medium text-[var(--text-muted)]">● Out of Stock</span>
              )}
            </div>

            {/* Variants */}
            {product.variants?.map((variant) => (
              <div key={variant.id} className="mt-5">
                <p className="text-sm font-semibold text-[var(--text-primary)] mb-2">{variant.label}</p>
                <div className="flex flex-wrap gap-2">
                  {variant.options.map((opt) => (
                    <button
                      key={opt}
                      onClick={() => setSelectedVariants((prev) => ({ ...prev, [variant.label]: opt }))}
                      className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${
                        selectedVariants[variant.label] === opt
                          ? "border-[var(--lt-primary)] bg-[var(--lt-primary)] text-white"
                          : "border-[var(--border)] hover:border-[var(--border-hover)]"
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            ))}

            {/* Actions */}
            <div className="mt-6 flex gap-3">
              <button
                onClick={() => addItem(product.id)}
                className="lt-btn lt-btn-lg lt-btn-primary flex-1"
                disabled={product.availability === "out-of-stock"}
              >
                <ShoppingBag size={18} />
                Add to Cart
              </button>
              <button
                onClick={() => addItem(product.id)}
                className="lt-btn lt-btn-lg lt-btn-accent flex-1"
                disabled={product.availability === "out-of-stock"}
              >
                <Zap size={18} />
                Buy Now
              </button>
            </div>

            <div className="mt-3 flex gap-2">
              <button className="lt-btn lt-btn-md lt-btn-ghost flex-1" aria-label="Add to wishlist">
                <Heart size={16} strokeWidth={1.5} /> Wishlist
              </button>
              <button onClick={handleShare} className="lt-btn lt-btn-md lt-btn-ghost flex-1" aria-label="Share product">
                <Share2 size={16} strokeWidth={1.5} /> Share
              </button>
            </div>

            {/* Delivery & returns */}
            <div className="mt-6 space-y-3 border-t border-[var(--border)] pt-5">
              {product.estimatedDelivery && (
                <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                  <Truck size={16} strokeWidth={1.5} />
                  <span>Estimated delivery: {product.estimatedDelivery}</span>
                </div>
              )}
              {product.returnInfo && (
                <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                  <RotateCcw size={16} strokeWidth={1.5} />
                  <span>{product.returnInfo}</span>
                </div>
              )}
            </div>

            {/* Description */}
            <div className="mt-6 border-t border-[var(--border)] pt-5">
              <h2 className="text-sm font-bold text-[var(--text-primary)] mb-2">Description</h2>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{product.description}</p>
            </div>

            {/* Specs */}
            {product.specs && product.specs.length > 0 && (
              <div className="mt-5 border-t border-[var(--border)] pt-5">
                <h2 className="text-sm font-bold text-[var(--text-primary)] mb-2">Specifications</h2>
                <dl className="space-y-2">
                  {product.specs.map((spec) => (
                    <div key={spec.label} className="flex justify-between text-sm">
                      <dt className="text-[var(--text-muted)]">{spec.label}</dt>
                      <dd className="text-[var(--text-primary)] font-medium">{spec.value}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}
          </div>
        </div>

        {/* Related Products */}
        {related.length > 0 && (
          <div className="mt-12 border-t border-[var(--border)] pt-10">
            <h2 className="lt-heading-2 mb-6">You might also like</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {related.map((p) => (
                <CommerceProductCard key={p.id} product={p} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
