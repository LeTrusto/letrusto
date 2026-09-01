"use client";

import Image from "next/image";
import Link from "next/link";
import { Heart, Plus } from "lucide-react";
import { useState } from "react";
import type { CommerceProduct } from "@/types/commerce";
import { useCart } from "@/lib/cartContext";

type Props = {
  product: CommerceProduct;
};

function formatPrice(value: number): string {
  return `₹${value.toLocaleString("en-IN")}`;
}

const PLACEHOLDER_IMAGE = "/images/products/placeholder.svg";

export default function CommerceProductCard({ product }: Props) {
  const { addItem } = useCart();
  const [imageFailed, setImageFailed] = useState(false);
  const selectedVariant = product.catalogVariants?.find((variant) => variant.available);
  const canAdd = product.catalogVariants?.length ? Boolean(selectedVariant) : product.availability !== "out-of-stock";
  const image = product.images[0];

  return (
    <div className="lt-card lt-card-hover group flex flex-col h-full p-0 overflow-hidden">
      {/* Image */}
      <Link href={`/product/${product.slug}`} className="relative aspect-square bg-[var(--surface-muted)] overflow-hidden">
        <Image
          src={imageFailed || !image ? PLACEHOLDER_IMAGE : image}
          alt={product.name}
          fill
          sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
          className="object-cover transition-transform duration-300 group-hover:scale-105"
          onError={() => setImageFailed(true)}
        />
        {/* Badges */}
        <div className="absolute top-2 left-2 flex flex-col gap-1">
          {product.isTrending && (
            <span className="lt-badge lt-badge-accent text-[10px]">Trending</span>
          )}
          {product.isNewDrop && (
            <span className="lt-badge text-[10px]">New</span>
          )}
          {product.compareAtPrice && (
            <span className="lt-badge lt-badge-sale text-[10px]">
              {Math.round(((product.compareAtPrice - product.price) / product.compareAtPrice) * 100)}% off
            </span>
          )}
        </div>
        {/* Wishlist */}
        <button
          className="absolute top-2 right-2 w-8 h-8 bg-white/80 backdrop-blur-sm rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white"
          aria-label={`Add ${product.name} to wishlist`}
        >
          <Heart size={14} strokeWidth={1.5} />
        </button>
      </Link>

      {/* Info */}
      <div className="flex flex-col flex-1 p-3">
        <span className="text-[10px] font-medium uppercase tracking-wider text-[var(--text-muted)]">
          {product.categoryLabel}
        </span>
        <Link href={`/product/${product.slug}`} className="mt-1 text-sm font-semibold text-[var(--text-primary)] line-clamp-2 leading-snug hover:underline">
          {product.name}
        </Link>
        <div className="mt-auto pt-2 flex items-center justify-between">
          <div className="flex items-baseline gap-1.5">
            <span className="text-base font-bold text-[var(--text-primary)]">{formatPrice(product.price)}</span>
            {product.compareAtPrice && (
              <span className="text-xs text-[var(--text-muted)] line-through">{formatPrice(product.compareAtPrice)}</span>
            )}
          </div>
          <button
            onClick={() => { if (canAdd) addItem(product.id, 1, selectedVariant?.id); }}
            disabled={!canAdd}
            className="w-8 h-8 rounded-full bg-[var(--lt-primary)] text-white flex items-center justify-center hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
            aria-label={`Add ${product.name} to cart`}
          >
            <Plus size={16} strokeWidth={2} />
          </button>
        </div>
      </div>
    </div>
  );
}
