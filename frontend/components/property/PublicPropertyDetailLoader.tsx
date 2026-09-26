"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { getPublicProperty, type PublicProperty } from "@/services/property.service";
import { PropertyDetail, PropertyUnavailable } from "./PropertyDetail";

export default function PublicPropertyDetailLoader() {
  const params = useParams<{ slug: string }>();
  const [property, setProperty] = useState<PublicProperty | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    void getPublicProperty(params.slug).then((result) => {
      if (!cancelled) {
        setProperty(result);
        setLoading(false);
      }
    });
    return () => { cancelled = true; };
  }, [params.slug]);

  if (loading) {
    return <main className="property-unavailable section-shell"><p className="eyebrow">Bangalore / Property journal</p><h1 className="display-title">Loading<br /><em>this place.</em></h1></main>;
  }

  return property ? <PropertyDetail property={property} /> : <PropertyUnavailable />;
}
