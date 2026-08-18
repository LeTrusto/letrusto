"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Check, Heart, Loader2, Minus, Plus, Share2, ShoppingBag, Truck, RotateCcw, ChevronLeft, Zap } from "lucide-react";
import type { CommerceProduct } from "@/types/commerce";
import { useCart } from "@/lib/cartContext";
import CommerceProductCard from "@/components/products/CommerceProductCard";
import SchemaOrg from "@/components/SchemaOrg";

function formatPrice(value: number): string {
  return `₹${value.toLocaleString("en-IN")}`;
}

type Props = {
  product: CommerceProduct;
  related: CommerceProduct[];
};

export default function ProductDetailView({ product, related }: Props) {
  const { addItem } = useCart();
  const router = useRouter();
  const [selectedVariantId, setSelectedVariantId] = useState(product.catalogVariants?.find((variant) => variant.available)?.id ?? null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [action, setAction] = useState<"cart" | "buy" | null>(null);
  const selectedVariant = product.catalogVariants?.find((variant) => variant.id === selectedVariantId);
  const displayPrice = selectedVariant?.price ?? product.price;
  const isAvailable = selectedVariant?.available ?? product.availability !== "out-of-stock";
  const maxQuantity = selectedVariant?.inventory ?? 1;
  const [quantity, setQuantity] = useState(1);

  const discount = product.compareAtPrice
    ? Math.round(((product.compareAtPrice - product.price) / product.compareAtPrice) * 100)
    : 0;

  function handleShare() {
    if (typeof navigator !== "undefined" && navigator.share) {
      navigator.share({ title: product.name, url: window.location.href }).catch(() => {});
    }
  }

  function addToCart() {
    if (!isAvailable || action) return;
    setAction("cart");
    addItem(product.id, quantity, selectedVariantId ?? undefined);
    window.setTimeout(() => setAction(null), 900);
  }

  function buyNow() {
    if (!isAvailable || action) return;
    setAction("buy");
    addItem(product.id, quantity, selectedVariantId ?? undefined);
    router.push("/checkout");
  }

  const activeImage = product.images[selectedImageIndex] ?? "/images/products/placeholder.svg";
  const productDescription = product.description.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();

  return (
    <main className="min-h-screen bg-white">
      <SchemaOrg
        type="Product"
        data={{
          name: product.name,
          image: product.images,
          description: productDescription,
          offers: {
            "@type": "Offer",
            url: `https://letrusto.com/product/${product.slug}`,
            priceCurrency: product.currency,
            price: displayPrice,
            availability: isAvailable ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
          },
        }}
      />
      {/* Breadcrumb */}
      <div className="max-w-7xl mx-auto px-4 md:px-6 py-3">
        <Link href="/shop" className="inline-flex items-center gap-1 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
          <ChevronLeft size={14} />
          Back to Shop
        </Link>
      </div>

      <div className="mx-auto max-w-7xl px-4 pb-10 md:px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12">
          {/* Images */}
          <section className="min-w-0" aria-label={`${product.name} images`}>
            <div className="relative aspect-square overflow-hidden rounded-xl bg-[var(--surface-muted)]">
              <Image
                key={activeImage}
                src={activeImage}
                alt={`${product.name}${product.images.length > 1 ? ` view ${selectedImageIndex + 1}` : ""}`}
                fill
                sizes="(max-width: 768px) 100vw, 50vw"
                className="object-cover"
                priority
              />
              {discount > 0 && <span className="lt-badge lt-badge-sale absolute left-3 top-3">{discount}% off</span>}
            </div>
            {product.images.length > 1 && (
              <div className="mt-3 grid grid-cols-4 gap-2 sm:grid-cols-6" aria-label="Select product image">
                {product.images.map((image, index) => (
                  <button
                    key={image}
                    type="button"
                    onClick={() => setSelectedImageIndex(index)}
                    className={`relative aspect-square min-w-0 overflow-hidden rounded-md border ${selectedImageIndex === index ? "border-[var(--lt-primary)] ring-2 ring-[var(--lt-primary)]/20" : "border-[var(--border)] hover:border-[var(--border-hover)]"}`}
                    aria-label={`Show ${product.name} image ${index + 1}`}
                    aria-pressed={selectedImageIndex === index}
                  >
                    <Image src={image} alt="" fill sizes="(max-width: 640px) 22vw, 96px" className="object-cover" />
                  </button>
                ))}
              </div>
            )}
          </section>

          {/* Details */}
          <div className="flex min-w-0 flex-col md:sticky md:top-20 md:self-start">
            <span className="lt-label text-[var(--text-muted)]">{product.categoryLabel}</span>
            <h1 className="mt-1 text-2xl md:text-3xl font-bold text-[var(--text-primary)] leading-tight">
              {product.name}
            </h1>

            {/* Price */}
            <div className="mt-4 flex flex-wrap items-baseline gap-x-2 gap-y-1">
              <span className="text-3xl font-bold text-[var(--text-primary)]">{formatPrice(displayPrice)}</span>
              {product.compareAtPrice && (
                <>
                  <span className="text-base text-[var(--text-muted)] line-through">{formatPrice(product.compareAtPrice)}</span>
                  <span className="text-sm font-semibold text-[var(--lt-rose)]">Save {formatPrice(product.compareAtPrice - product.price)}</span>
                </>
              )}
            </div>

            {/* Availability */}
            <div className="mt-3" aria-live="polite">
              {isAvailable && (
                <span className="text-sm font-medium text-[var(--lt-success)]">● In Stock</span>
              )}
              {!isAvailable && (
                <span className="text-sm font-medium text-[var(--text-muted)]">● This option is unavailable</span>
              )}
            </div>

            {/* Variants */}
            {product.catalogVariants && product.catalogVariants.length > 0 && (
              <div className="mt-5">
                <p className="mb-2 text-sm font-semibold text-[var(--text-primary)]">Choose an option</p>
                <div className="flex flex-wrap gap-2">
                  {product.catalogVariants.map((variant) => (
                    <button
                      key={variant.id}
                      type="button"
                      disabled={!variant.available}
                      onClick={() => { setSelectedVariantId(variant.id); setQuantity(1); }}
                      className={`max-w-full break-words px-3 py-1.5 text-left text-sm rounded-md border transition-colors ${
                        selectedVariantId === variant.id
                          ? "border-[var(--lt-primary)] bg-[var(--lt-primary)] text-white"
                          : variant.available ? "border-[var(--border)] hover:border-[var(--border-hover)]" : "border-[var(--border)] text-[var(--text-muted)] line-through"
                      }`}
                    >
                      <span>{variant.label}</span><span className="text-xs opacity-80">{formatPrice(variant.price)}</span>{!variant.available && <span className="text-xs">Unavailable</span>}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            {isAvailable && (
              <div className="mt-5 flex flex-wrap items-center gap-3 text-sm font-semibold">
                <span>Quantity</span>
                <div className="flex items-center rounded-md border border-[var(--border)]">
                  <button type="button" onClick={() => setQuantity((current) => Math.max(1, current - 1))} className="flex h-10 w-10 items-center justify-center hover:bg-[var(--surface-muted)]" aria-label={`Decrease quantity for ${product.name}`}><Minus size={15} /></button>
                <input
                  type="number"
                  min={1}
                  max={maxQuantity}
                  value={quantity}
                  onChange={(event) => setQuantity(Math.min(maxQuantity, Math.max(1, Number(event.target.value) || 1)))}
                  className="h-10 w-14 rounded-none border-x border-y-0 border-[var(--border)] px-1 text-center"
                  aria-label={`Quantity for ${product.name}`}
                />
                  <button type="button" onClick={() => setQuantity((current) => Math.min(maxQuantity, current + 1))} disabled={quantity >= maxQuantity} className="flex h-10 w-10 items-center justify-center hover:bg-[var(--surface-muted)]" aria-label={`Increase quantity for ${product.name}`}><Plus size={15} /></button>
                </div>
              </div>
            )}
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={addToCart}
                className="lt-btn lt-btn-lg lt-btn-primary w-full"
                disabled={!isAvailable || action !== null}
              >
                {action === "cart" ? <><Check size={18} /> Added to cart</> : <><ShoppingBag size={18} /> Add to Cart</>}
              </button>
              <button
                type="button"
                onClick={buyNow}
                className="lt-btn lt-btn-lg lt-btn-accent w-full"
                disabled={!isAvailable || action !== null}
              >
                {action === "buy" ? <><Loader2 size={18} className="animate-spin" /> Continuing...</> : <><Zap size={18} /> Buy Now</>}
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
                  <span>{product.estimatedDelivery}</span>
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
    </main>
  );
}
