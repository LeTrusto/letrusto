import Link from "next/link";
import Image from "next/image";
import { ArrowUpRight } from "lucide-react";

import type { MockProperty } from "@/lib/propertyMockData";
import type { PublicProperty } from "@/services/property.service";
import { verificationBadgeLabel } from "@/utils/verification";

type CardProperty = PublicProperty | MockProperty;

function isPublicProperty(property: CardProperty): property is PublicProperty {
  return "property_type" in property;
}

function typeLabel(property: CardProperty): string {
  if (!isPublicProperty(property)) return property.type;
  return property.property_type.replaceAll("_", " ").replace(/(^| )\w/g, (letter) => letter.toUpperCase());
}

function cardImage(property: CardProperty): string | null {
  if (!isPublicProperty(property)) return property.image;
  return property.media.find((media) => media.is_cover && media.media_type === "IMAGE" && media.public_url)?.public_url
    ?? property.media.find((media) => media.media_type === "IMAGE" && media.public_url)?.public_url
    ?? null;
}

function cardArea(property: CardProperty): string | null {
  if (!isPublicProperty(property)) return property.area;
  const area = property.built_up_area_sqft ?? property.carpet_area_sqft ?? property.plot_area_sqft;
  return area ? `${Number(area).toLocaleString("en-IN")} sq.ft` : null;
}

function cardPrice(property: CardProperty): string {
  if (!isPublicProperty(property)) return property.price;
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: property.currency, maximumFractionDigits: 0 }).format(Number(property.price_amount));
}

function cardRegion(property: CardProperty): string {
  return isPublicProperty(property) ? property.location.city_name : property.region;
}

export function PropertyCard({ property, featured = false }: { property: CardProperty; featured?: boolean }) {
  const image = cardImage(property);
  const locality = isPublicProperty(property) ? property.location.name : property.locality;
  const trustLabel = isPublicProperty(property) ? verificationBadgeLabel(property.verification) : null;
  const badge = isPublicProperty(property) ? trustLabel : property.badge;
  return (
    <article className={`property-card group ${featured ? "property-card-featured" : ""}`}>
      <Link href={`/properties/${property.slug}`} className="block h-full" aria-label={`Explore ${property.title} in ${locality}`}>
        <div className="property-card-image-wrap">
          {image ? <Image src={image} alt={`${property.title}, ${locality}`} fill sizes={featured ? "(max-width: 560px) 92vw, 470px" : "(max-width: 560px) 88vw, 340px"} className="property-card-image" priority={featured} unoptimized={isPublicProperty(property)} /> : <div className="property-card-no-image">Photos coming soon.</div>}
          <div className="property-card-wash" />
          {badge && <span className="property-badge property-badge-terracotta">{badge}</span>}
          <span className="property-arrow" aria-hidden="true"><ArrowUpRight size={18} strokeWidth={1.7} /></span>
          <div className="property-card-overlay-copy">
            <span>{typeLabel(property)}</span>
            <h3>{property.title}</h3>
          </div>
        </div>
        <div className="property-card-meta">
          <div>
            <p className="property-card-place">{locality} <span>/</span> {cardRegion(property)}</p>
            <p className="property-card-description">{property.description}</p>
          </div>
          <div className="property-card-price">
            <strong>{cardPrice(property)}</strong>
            <span>{property.bhk ? `${isPublicProperty(property) ? `${property.bhk} BHK` : property.bhk} · ` : ""}{cardArea(property)}</span>
          </div>
        </div>
      </Link>
    </article>
  );
}
