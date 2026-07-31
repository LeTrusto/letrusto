"use client";

import clsx from "clsx";
import { Heart, Scale } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { memo, useMemo, useState } from "react";
import { motion } from "framer-motion";

import { useFavorites } from "@/hooks/useFavorites";
import { categoryLabels } from "@/lib/products";
import { getCompareHref } from "@/services/product.service";
import type { Product } from "@/types/products";

type ProductCardProps = {
  product: Product;
  compareWithId?: string;
  highlightLabel?: string;
  className?: string;
  priority?: boolean;
};

function ProductCard({
  product,
  compareWithId,
  highlightLabel,
  className,
  priority = false,
}: ProductCardProps) {
  const { isFavorite, toggleFavorite } = useFavorites();
  const favorite = isFavorite(product.id);
  const [hasImageError, setHasImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const imageSrc = hasImageError ? product.fallbackImage : product.image;
  const isLocalProductImage = useMemo(() => imageSrc.startsWith("/images/products/"), [imageSrc]);

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.32, ease: "easeOut" }}
      className={clsx(
        "group overflow-hidden rounded-3xl border border-purple-100 bg-white premium-shadow transition duration-300 hover:-translate-y-1 hover:shadow-[0_30px_70px_rgba(71,38,211,0.2)]",
        className
      )}
    >
      <div className="relative bg-gradient-to-br from-pink-50 via-white to-purple-50 p-6">
        <div className="flex items-start justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-purple-700">
              {categoryLabels[product.category]}
            </span>
            {highlightLabel ? (
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
                {highlightLabel}
              </span>
            ) : null}
          </div>

          <button
            type="button"
            onClick={() => toggleFavorite(product.id)}
            aria-label={favorite ? `Remove ${product.name} from favorites` : `Add ${product.name} to favorites`}
            className={clsx(
              "inline-flex h-11 w-11 items-center justify-center rounded-full border transition focus-visible:ring-2 focus-visible:ring-purple-500",
              favorite
                ? "border-pink-200 bg-pink-50 text-pink-600"
                : "border-white/80 bg-white/90 text-gray-500 hover:text-pink-600"
            )}
          >
            <Heart className={clsx("h-5 w-5", favorite && "fill-current")} />
          </button>
        </div>

        <Image
          src={imageSrc}
          alt={product.name}
          width={280}
          height={280}
          unoptimized={isLocalProductImage}
          priority={priority}
          loading={priority ? "eager" : "lazy"}
          onLoad={() => setImageLoaded(true)}
          onError={() => {
            setHasImageError(true);
            setImageLoaded(true);
          }}
          className={clsx(
            "mx-auto mt-6 h-52 w-auto object-contain transition duration-200 group-hover:scale-105",
            imageLoaded || isLocalProductImage ? "opacity-100" : "opacity-0"
          )}
        />
        {!imageLoaded && !isLocalProductImage ? <div className="absolute inset-x-8 bottom-6 h-52 rounded-2xl shimmer" aria-hidden="true" /> : null}
      </div>

      <div className="space-y-5 p-6">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">{product.name}</h3>
          <p className="mt-2 text-sm leading-6 text-gray-500">{product.description}</p>
        </div>

        <div className="flex items-end justify-between gap-4 rounded-2xl bg-gray-50 px-4 py-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">Price</p>
            <p className="mt-1 text-2xl font-bold text-purple-600">{product.price}</p>
          </div>

          <div className="text-right">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">Rating</p>
            <p className="mt-1 text-lg font-semibold text-amber-500">{product.rating.toFixed(1)} / 5</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm font-medium text-gray-700">
          <div className="rounded-2xl bg-purple-50 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-purple-500">AI Score</p>
            <p className="mt-1 text-2xl font-extrabold text-purple-700">{product.aiScore}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Top Feature</p>
            <p className="mt-1 line-clamp-2 text-sm text-slate-700">{product.features[0]}</p>
          </div>
        </div>

        <div className="flex gap-3">
          <Link
            href={`/products/${product.id}`}
            className="inline-flex flex-1 items-center justify-center rounded-2xl bg-gradient-to-r from-fuchsia-600 to-purple-600 px-4 py-3 font-semibold text-white transition hover:from-fuchsia-700 hover:to-purple-700"
          >
            View Details
          </Link>
          <Link
            href={getCompareHref(product.id, compareWithId)}
            className="inline-flex flex-1 items-center justify-center gap-2 rounded-2xl border border-purple-200 px-4 py-3 font-semibold text-purple-700 transition hover:bg-purple-50"
          >
            <Scale className="h-4 w-4" />
            Compare
          </Link>
        </div>
      </div>
    </motion.article>
  );
}

export default memo(ProductCard);
