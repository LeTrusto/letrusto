import type { Metadata } from "next";

import PublicPropertyDetailLoader from "@/components/property/PublicPropertyDetailLoader";
import { getPublicProperty } from "@/services/property.service";

export const dynamic = "force-dynamic";

function detailDescription(title: string, locality: string, description: string): string {
  return `${title} in ${locality}, Bengaluru. ${description}`;
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const property = await getPublicProperty(slug);
  if (!property) {
    return { title: "Property unavailable", description: "Explore available properties across Bengaluru.", robots: { index: false, follow: true } };
  }

  const description = detailDescription(property.title, property.location.name, property.description);
  return {
    title: property.title,
    description,
    alternates: { canonical: `/properties/${property.slug}` },
    openGraph: { title: property.title, description, type: "website", url: `/properties/${property.slug}` },
  };
}

export default function PropertyDetailPage() {
  return <PublicPropertyDetailLoader />;
}
