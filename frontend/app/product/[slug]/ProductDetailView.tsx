"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { Check, Heart, Loader2, Minus, Plus, Share2, ShoppingBag, Truck, RotateCcw, ChevronLeft, Zap } from "lucide-react";
import type { CommerceProduct } from "@/types/commerce";
import { useCart } from "@/lib/cartContext";
import CommerceProductCard from "@/components/products/CommerceProductCard";
import ProductTrustSection from "@/components/products/ProductTrustSection";
import SchemaOrg from "@/components/SchemaOrg";
import { buildApiUrl } from "@/services/api";
import { SITE_URL } from "@/config/site";

function formatPrice(value: number): string {
  return `₹${value.toLocaleString("en-IN")}`;
}

type Props = {
  product: CommerceProduct;
  related: CommerceProduct[];
};

type ShippingEstimate = {
  status: "AVAILABLE" | "REQUIRES_VERIFICATION";
  currency?: string | null;
  shipping_method?: string | null;
  shipping_price?: number | string | null;
  message?: string | null;
  estimated_delivery?: string | null;
  estimated?: boolean;
};

type ShippingState = "loading" | "ready" | "error";

const PLACEHOLDER_IMAGE = "/images/products/placeholder.svg";

export default function ProductDetailView({ product, related }: Props) {
  const { addItem } = useCart();
  const router = useRouter();
  const [selectedVariantId, setSelectedVariantId] = useState(product.catalogVariants?.find((variant) => variant.available)?.id ?? null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [action, setAction] = useState<"cart" | "buy" | null>(null);
  const actionLocked = useRef(false);
  const selectedVariant = product.catalogVariants?.find((variant) => variant.id === selectedVariantId);
  const displayPrice = selectedVariant?.price ?? product.price;
  const isAvailable = selectedVariant ? selectedVariant.available && selectedVariant.inventory > 0 : product.availability !== "out-of-stock";
  const maxQuantity = Math.max(1, selectedVariant?.inventory ?? 1);
  const [quantity, setQuantity] = useState(1);
  const [shippingCountry, setShippingCountry] = useState("IN");
  const [shippingResult, setShippingResult] = useState<{ key: string; estimate: ShippingEstimate | null; error: boolean } | null>(null);
  const [failedImages, setFailedImages] = useState<Set<string>>(() => new Set());
  const shippingKey = `${product.id}|${shippingCountry}|${quantity}`;
  const shippingState: ShippingState = shippingResult?.key === shippingKey ? shippingResult.estimate ? "ready" : "error" : "loading";
  const shippingEstimate = shippingResult?.key === shippingKey ? shippingResult.estimate : null;

  const discount = product.compareAtPrice
    ? Math.round(((product.compareAtPrice - product.price) / product.compareAtPrice) * 100)
    : 0;

  function handleShare() {
    if (typeof navigator !== "undefined" && navigator.share) {
      navigator.share({ title: product.name, url: window.location.href }).catch(() => {});
    }
  }

  function addToCart() {
    if (!isAvailable || action || actionLocked.current) return;
    actionLocked.current = true;
    setAction("cart");
    addItem(product.id, quantity, selectedVariantId ?? undefined);
    window.setTimeout(() => { actionLocked.current = false; setAction(null); }, 900);
  }

  function buyNow() {
    if (!isAvailable || action || actionLocked.current) return;
    actionLocked.current = true;
    setAction("buy");
    addItem(product.id, quantity, selectedVariantId ?? undefined);
    router.push("/checkout");
  }

  const rawActiveImage = product.images[selectedImageIndex] ?? PLACEHOLDER_IMAGE;
  const activeImage = failedImages.has(rawActiveImage) ? PLACEHOLDER_IMAGE : rawActiveImage;
  const productDescription = product.description.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();

  function imageSource(image: string | undefined) {
    if (!image) return PLACEHOLDER_IMAGE;
    return failedImages.has(image) ? PLACEHOLDER_IMAGE : image;
  }

  function markImageFailed(image: string) {
    if (image === PLACEHOLDER_IMAGE) return;
    setFailedImages((current) => new Set(current).add(image));
  }

  function shippingMessage() {
    if (shippingState === "loading") return "Checking current shipping rate...";
    if (shippingState === "error") return "Shipping could not be checked right now. The final charge is confirmed at checkout.";
    if (shippingEstimate?.status === "REQUIRES_VERIFICATION") return shippingEstimate.message ?? "Shipping rate requires Printful verification";
    if (shippingEstimate?.status === "AVAILABLE") return `${shippingEstimate.estimated ? "Estimated shipping: " : "Shipping: "}${shippingEstimate.currency === "INR" ? "₹" : "$"}${Number(shippingEstimate.shipping_price ?? 0).toFixed(2)}${shippingEstimate.shipping_method && !shippingEstimate.estimated ? ` · ${shippingEstimate.shipping_method}` : ""}`;
    return "Shipping estimate unavailable.";
  }

  useEffect(() => {
    const controller = new AbortController();
    fetch(buildApiUrl(`/products/${encodeURIComponent(product.id)}/shipping?country=${shippingCountry}&quantity=${quantity}`), { signal: controller.signal })
      .then((response) => response.ok ? response.json() as Promise<ShippingEstimate> : Promise.reject(new Error("Shipping unavailable")))
      .then((estimate) => { setShippingResult({ key: shippingKey, estimate, error: false }); })
      .catch((error: unknown) => { if (error instanceof DOMException && error.name === "AbortError") return; setShippingResult({ key: shippingKey, estimate: null, error: true }); });
    return () => controller.abort();
  }, [product.id, quantity, shippingCountry, shippingKey]);

  return (
    <main className="min-h-screen bg-[var(--background)]">
      <SchemaOrg
        type="Product"
        data={{
          name: product.name,
          image: product.images,
          description: productDescription,
          offers: {
            "@type": "Offer",
            url: `${SITE_URL}/product/${product.slug}`,
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
                onError={() => markImageFailed(rawActiveImage)}
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
                    <Image src={imageSource(image)} alt="" fill sizes="(max-width: 640px) 22vw, 96px" className="object-cover" onError={() => markImageFailed(image)} />
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

            <section className="mt-5 border-y border-[var(--border)] py-4" aria-label="Shipping estimate" aria-live="polite">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h2 className="text-sm font-bold text-[var(--text-primary)]">Shipping</h2>
                <label className="text-xs text-[var(--text-muted)]">Deliver to <select value={shippingCountry} onChange={(event) => setShippingCountry(event.target.value)} className="ml-1 rounded-md border border-[var(--border)] bg-[var(--background)] px-2 py-1 text-[var(--text-primary)]"><option value="IN">India</option><option value="US">United States</option><option value="GB">United Kingdom</option><option value="DE">European Union</option><option value="CA">Canada</option><option value="AU">Australia</option><option value="NZ">New Zealand</option><option value="JP">Japan</option><option value="BR">Brazil</option></select></label>
              </div>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">
                {shippingMessage()}
              </p>
              {shippingEstimate?.estimated_delivery && <p className="mt-1 text-xs text-[var(--text-muted)]">Estimated delivery: {shippingEstimate.estimated_delivery}</p>}
            </section>

            {/* Variants */}
            {product.catalogVariants && product.catalogVariants.length > 0 && (
              <div className="mt-5">
                <p className="mb-2 text-sm font-semibold text-[var(--text-primary)]">Choose an option</p>
                <div className="flex flex-wrap gap-2">
                  {product.catalogVariants.map((variant) => (
                    <button
                      key={variant.id}
                      type="button"
                      disabled={!variant.available || variant.inventory <= 0}
                      onClick={() => { setSelectedVariantId(variant.id); setQuantity(1); }}
                      className={`max-w-full break-words px-3 py-1.5 text-left text-sm rounded-md border transition-colors ${
                        selectedVariantId === variant.id
                          ? "border-[var(--lt-primary)] bg-[var(--lt-primary)] text-white"
                          : variant.available ? "border-[var(--border)] hover:border-[var(--border-hover)]" : "border-[var(--border)] text-[var(--text-muted)] line-through"
                      }`}
                    >
                      <span className="block font-semibold">{variant.label}</span><span className="block text-xs opacity-80">{formatPrice(variant.price)}</span>{(!variant.available || variant.inventory <= 0) && <span className="block text-xs">Unavailable</span>}
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
                  <button type="button" onClick={() => setQuantity((current) => Math.max(1, current - 1))} disabled={quantity <= 1} className="flex h-10 w-10 items-center justify-center hover:bg-[var(--surface-muted)] disabled:cursor-not-allowed disabled:opacity-50" aria-label={`Decrease quantity for ${product.name}`}><Minus size={15} /></button>
                <input
                  type="number"
                  min={1}
                  max={maxQuantity}
                  value={quantity}
                  onChange={(event) => setQuantity(Math.min(maxQuantity, Math.max(1, Number(event.target.value) || 1)))}
                  className="h-10 w-14 rounded-none border-x border-y-0 border-[var(--border)] px-1 text-center"
                  aria-label={`Quantity for ${product.name}`}
                />
                  <button type="button" onClick={() => setQuantity((current) => Math.min(maxQuantity, current + 1))} disabled={quantity >= maxQuantity} className="flex h-10 w-10 items-center justify-center hover:bg-[var(--surface-muted)] disabled:cursor-not-allowed disabled:opacity-50" aria-label={`Increase quantity for ${product.name}`}><Plus size={15} /></button>
                </div>
                <span className="text-xs text-[var(--text-muted)]">{maxQuantity} available</span>
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
                  <span>Made-to-order product. Returns are limited to eligible damaged, defective, incorrect, or materially mismatched items. <Link className="underline" href="/returns-policy">See Returns &amp; Refunds</Link>.</span>
                </div>
              )}
            </div>

            {/* Description */}
            <div className="mt-6 border-t border-[var(--border)] pt-5">
              <h2 className="text-sm font-bold text-[var(--text-primary)] mb-2">Description</h2>
              <p className="break-words text-sm text-[var(--text-secondary)] leading-relaxed">{product.description}</p>
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

            <ProductTrustSection productId={product.id} />
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
