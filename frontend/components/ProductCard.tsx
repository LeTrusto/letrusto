"use client";

import clsx from "clsx";
import { Heart, Scale, Star, Sparkles, TrendingUp, Zap } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { memo, useMemo, useState } from "react";
import { motion } from "framer-motion";

import { useFavorites } from "@/hooks/useFavorites";
import { categoryLabels } from "@/lib/products";
import { getCompareHref } from "@/services/product.service";
import type { Product } from "@/types/products";

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={clsx(
            "h-3.5 w-3.5",
            star <= Math.round(rating) ? "fill-amber-400 text-amber-400" : "fill-gray-100 text-gray-200"
          )}
        />
      ))}
    </div>
  );
}

function AiScoreBadge({ score }: { score: number }) {
  const color =
    score >= 95 ? "bg-emerald-500" :
    score >= 88 ? "bg-blue-500" :
    score >= 80 ? "bg-purple-500" : "bg-gray-400";
  return (
    <div className={`flex items-center gap-1 rounded-full ${color} px-2 py-0.5 text-[11px] font-bold text-white`}>
      <Sparkles className="h-3 w-3" />
      {score}
    </div>
  );
}

type ProductCardProps = {
  product: Product;
  compareWithId?: string;
  highlightLabel?: string;
  aiHighlights?: string[];
  aiReason?: string;
  className?: string;
  priority?: boolean;
};

function ProductCard({
  product,
  compareWithId,
  highlightLabel,
  aiHighlights,
  aiReason,
  className,
  priority = false,
}: ProductCardProps) {
  const { isFavorite, toggleFavorite } = useFavorites();
  const favorite = isFavorite(product.id);
  const [hasImageError, setHasImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const imageSrc = hasImageError ? product.fallbackImage : product.image;
  const isLocalProductImage = useMemo(() => imageSrc.startsWith("/images/products/"), [imageSrc]);
  const resolvedHighlights = (aiHighlights && aiHighlights.length > 0 ? aiHighlights : product.pros)
    .map((item) => item.trim())
    .filter((item) => item.length > 0)
    .slice(0, 3);

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.32, ease: "easeOut" }}
      className={clsx(
        "group overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-indigo-100/60",
        className
      )}
    >
      {/* Image area */}
      <div className="relative bg-gradient-to-br from-slate-50 via-white to-indigo-50/40 p-5">
        {/* Badges top-left */}
        <div className="absolute left-3 top-3 flex flex-col gap-1.5">
          {highlightLabel === "AI Pick" && (
            <span className="flex items-center gap-1 rounded-full bg-violet-600 px-2.5 py-0.5 text-[11px] font-bold text-white">
              <Sparkles className="h-3 w-3" /> AI Pick
            </span>
          )}
          {highlightLabel === "Trending" && (
            <span className="flex items-center gap-1 rounded-full bg-orange-500 px-2.5 py-0.5 text-[11px] font-bold text-white">
              <TrendingUp className="h-3 w-3" /> Trending
            </span>
          )}
          {highlightLabel === "New" && (
            <span className="flex items-center gap-1 rounded-full bg-blue-600 px-2.5 py-0.5 text-[11px] font-bold text-white">
              <Zap className="h-3 w-3" /> New
            </span>
          )}
          {highlightLabel && !["AI Pick","Trending","New"].includes(highlightLabel) && (
            <span className="rounded-full bg-emerald-500 px-2.5 py-0.5 text-[11px] font-bold text-white">
              {highlightLabel}
            </span>
          )}
        </div>

        {/* Wishlist */}
        <button
          type="button"
          onClick={() => toggleFavorite(product.id)}
          aria-label={favorite ? `Remove ${product.name} from favorites` : `Add ${product.name} to favorites`}
          className={clsx(
            "absolute right-3 top-3 inline-flex h-9 w-9 items-center justify-center rounded-full border transition",
            favorite ? "border-pink-200 bg-pink-50 text-pink-600" : "border-gray-100 bg-white text-gray-400 hover:text-pink-500"
          )}
        >
          <Heart className={clsx("h-4 w-4", favorite && "fill-current")} />
        </button>

        <Image
          src={imageSrc}
          alt={product.name}
          width={240}
          height={200}
          unoptimized={isLocalProductImage}
          priority={priority}
          loading={priority ? "eager" : "lazy"}
          onLoad={() => setImageLoaded(true)}
          onError={() => { setHasImageError(true); setImageLoaded(true); }}
          className={clsx(
            "mx-auto h-40 w-auto object-contain transition duration-300 group-hover:scale-105",
            imageLoaded || isLocalProductImage ? "opacity-100" : "opacity-0"
          )}
        />
        {!imageLoaded && !isLocalProductImage && (
          <div className="absolute inset-x-6 top-12 h-40 rounded-xl shimmer" aria-hidden="true" />
        )}
      </div>

      {/* Content */}
      <div className="p-4 md:p-5">
        {/* Category + AI score */}
        <div className="mb-2.5 flex items-center justify-between gap-2">
          <span className="rounded-full bg-violet-50 px-2.5 py-0.5 text-[11px] font-semibold text-violet-700">
            {categoryLabels[product.category] ?? product.category}
          </span>
          <AiScoreBadge score={product.aiScore} />
        </div>

        {/* Name */}
        <h3 className="line-clamp-2 text-base font-black leading-snug tracking-tight text-slate-900 group-hover:text-violet-700">
          {product.name}
        </h3>
        <p className="mt-0.5 text-xs font-medium text-slate-400">{product.brand}</p>

        {resolvedHighlights.length > 0 || aiReason ? (
          <div className="mt-2.5 rounded-xl border border-violet-100 bg-violet-50/60 px-3 py-2 text-xs text-violet-900">
            <p className="font-semibold text-violet-800">Why AI recommends</p>
            {resolvedHighlights.length > 0 ? (
              <ul className="mt-1.5 space-y-1">
                {resolvedHighlights.map((point) => (
                  <li key={`${product.id}-${point}`} className="line-clamp-1">
                    {`\u2713 ${point}`}
                  </li>
                ))}
              </ul>
            ) : aiReason ? (
              <p className="mt-1.5 line-clamp-2 leading-relaxed">{aiReason}</p>
            ) : null}
          </div>
        ) : null}

        {/* Rating + price */}
        <div className="mt-3 flex items-end justify-between gap-2">
          <div>
            <StarRating rating={Number(product.rating)} />
            <span className="mt-0.5 block text-xs text-gray-400">{Number(product.rating).toFixed(1)} / 5</span>
          </div>
          <div className="text-right">
            <div className="text-lg font-black text-gray-900">{product.price}</div>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-4 flex gap-2">
          <Link
            href={`/products/${product.id}`}
            className="flex flex-1 items-center justify-center rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-600 py-2.5 text-sm font-bold text-white transition hover:scale-[1.02]"
          >
            View Details
          </Link>
          <Link
            href={getCompareHref(product.id, compareWithId)}
            className="flex items-center justify-center rounded-xl border border-gray-200 px-3 py-2.5 text-gray-500 transition hover:border-purple-300 hover:text-purple-600"
            aria-label="Compare"
          >
            <Scale className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </motion.article>
  );
}

export default memo(ProductCard);
