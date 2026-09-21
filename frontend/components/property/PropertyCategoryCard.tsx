import Link from "next/link";
import Image from "next/image";
import { ArrowUpRight } from "lucide-react";

import type { PropertyType } from "@/lib/propertyMockData";

export function PropertyCategoryCard({ category }: { category: { label: string; note: string; type: PropertyType; image: string; count: string } }) {
  return (
    <Link href={`/properties?type=${category.type.toLowerCase()}`} className="category-card group">
      <Image src={category.image} alt="" fill sizes="(max-width: 560px) 50vw, 25vw" className="category-card-image" />
      <div className="category-card-overlay" />
      <div className="category-card-copy"><span>{category.count} places</span><h3>{category.label}</h3><p>{category.note}</p></div>
      <span className="category-card-arrow" aria-hidden="true"><ArrowUpRight size={20} /></span>
    </Link>
  );
}
