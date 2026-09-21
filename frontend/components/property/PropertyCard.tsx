import Link from "next/link";
import Image from "next/image";
import { ArrowUpRight } from "lucide-react";

import type { MockProperty } from "@/lib/propertyMockData";

export function PropertyCard({ property, featured = false }: { property: MockProperty; featured?: boolean }) {
  return (
    <article className={`property-card group ${featured ? "property-card-featured" : ""}`}>
      <Link href={`/properties/${property.slug}`} className="block h-full" aria-label={`Explore ${property.title} in ${property.locality}`}>
        <div className="property-card-image-wrap">
          <Image src={property.image} alt={`${property.title}, ${property.locality}`} fill sizes={featured ? "(max-width: 560px) 92vw, 470px" : "(max-width: 560px) 88vw, 340px"} className="property-card-image" priority={featured} />
          <div className="property-card-wash" />
          <span className={`property-badge property-badge-${property.accent}`}>{property.badge}</span>
          <span className="property-arrow" aria-hidden="true"><ArrowUpRight size={18} strokeWidth={1.7} /></span>
          <div className="property-card-overlay-copy">
            <span>{property.type}</span>
            <h3>{property.title}</h3>
          </div>
        </div>
        <div className="property-card-meta">
          <div>
            <p className="property-card-place">{property.locality} <span>/</span> {property.region}</p>
            <p className="property-card-description">{property.description}</p>
          </div>
          <div className="property-card-price">
            <strong>{property.price}</strong>
            <span>{property.bhk ? `${property.bhk} · ` : ""}{property.area}</span>
          </div>
        </div>
      </Link>
    </article>
  );
}
