"use client";

import { useEffect } from "react";
import { trackSafeEvent } from "@/lib/analytics";
import type { DigitalProduct } from "@/types/digital-products";

export default function DigitalProductViewTracker({ product }: { product: DigitalProduct }) {
  useEffect(() => {
    trackSafeEvent("digital_product_view", { product_name: product.name, product_slug: product.slug });
  }, [product.name, product.slug]);

  return null;
}
