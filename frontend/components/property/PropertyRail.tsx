"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { getPublicProperties, type PublicProperty } from "@/services/property.service";
import { PropertyCard } from "./PropertyCard";

export function PropertyRail({ title = "The latest finds", eyebrow = "From the collection" }: { title?: string; eyebrow?: string }) {
  const [properties, setProperties] = useState<PublicProperty[]>([]);

  useEffect(() => {
    let cancelled = false;
    void getPublicProperties({ page_size: 5, sort: "newest" }).then((result) => {
      if (!cancelled) setProperties(result.items);
    }).catch(() => undefined);
    return () => { cancelled = true; };
  }, []);

  return (
    <section className="rail-section" aria-labelledby="latest-finds">
      <div className="section-shell rail-heading-row">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h2 id="latest-finds" className="display-title display-title-small">{title}</h2>
        </div>
        <Link href="/properties" className="text-link">See the full collection <ArrowRight size={16} /></Link>
      </div>
      <div className="property-rail" tabIndex={0} aria-label="Scrollable property collection">
        {properties.map((property) => <PropertyCard key={property.slug} property={property} />)}
      </div>
    </section>
  );
}
