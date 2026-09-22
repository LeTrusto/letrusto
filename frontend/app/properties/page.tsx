import type { Metadata } from "next";
import { Suspense } from "react";

import { PropertyDiscovery } from "@/components/property/PropertyDiscovery";

export const metadata: Metadata = { title: "The collection", description: "A considered collection of Bangalore properties." };

export default function PropertiesPage() {
  return <Suspense fallback={<main className="collection-page discovery-page"><div className="discovery-state"><h2>Finding live properties across Bengaluru.</h2></div></main>}><PropertyDiscovery /></Suspense>;
}
