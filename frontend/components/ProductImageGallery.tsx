"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";

type ProductImageGalleryProps = {
  name: string;
  images: string[];
  fallbackImage: string;
};

export default function ProductImageGallery({
  name,
  images,
  fallbackImage,
}: ProductImageGalleryProps) {
  const [activeImage, setActiveImage] = useState(images[0]);
  const [imageLoaded, setImageLoaded] = useState(false);
  const isLocalProductImage = activeImage.startsWith("/images/products/");

  return (
    <div className="min-w-0 space-y-5 rounded-[2rem] bg-white p-8 premium-shadow">
      <div className="relative overflow-hidden rounded-[2rem] bg-gradient-to-br from-pink-50 via-white to-purple-50 p-8">
        {!imageLoaded && !isLocalProductImage ? <div className="absolute inset-8 rounded-3xl shimmer" aria-hidden="true" /> : null}
        <Image
          src={activeImage}
          alt={name}
          width={680}
          height={680}
          unoptimized={isLocalProductImage}
          priority
          loading="eager"
          onLoad={() => setImageLoaded(true)}
          onError={() => {
            if (activeImage !== fallbackImage) {
              setActiveImage(fallbackImage);
            }
            setImageLoaded(true);
          }}
          className="mx-auto h-[22rem] w-auto object-contain transition duration-200 hover:scale-110 md:h-[28rem]"
        />
      </div>

      <div className="flex gap-4 overflow-x-auto pb-2" role="tablist" aria-label="Product images">
        {images.map((image, index) => (
          <motion.button
            key={`${image}-${index}`}
            type="button"
            onClick={() => {
              setImageLoaded(false);
              setActiveImage(image);
            }}
            whileHover={{ y: -2 }}
            role="tab"
            aria-selected={activeImage === image}
            className={`min-w-28 rounded-2xl border p-3 transition ${
              activeImage === image
                ? "border-purple-400 bg-purple-50"
                : "border-gray-200 bg-white hover:border-purple-200"
            }`}
          >
            <Image
              src={image}
              alt={`${name} view ${index + 1}`}
              width={180}
              height={180}
              unoptimized={image.startsWith("/images/products/")}
              loading="eager"
              className="mx-auto h-20 w-auto object-contain"
            />
          </motion.button>
        ))}
      </div>
    </div>
  );
}
