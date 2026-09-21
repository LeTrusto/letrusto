import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, ArrowRight } from "lucide-react";

import { properties } from "@/lib/propertyMockData";
import { PropertyCard } from "@/components/property/PropertyCard";

export const metadata: Metadata = { title: "The collection", description: "A considered collection of Bangalore properties." };

export default function PropertiesPage() {
  return <main className="collection-page"><nav className="site-nav collection-nav section-shell"><Link href="/" className="temporary-mark"><span className="mark-dot" />BENGALURU PROPERTY</Link><div className="nav-links"><Link href="/">Home</Link><span className="nav-current">The collection</span><Link href="/login">For sellers</Link></div><Link href="/" className="nav-pill"><ArrowLeft size={15} /> Home</Link></nav><header className="collection-header section-shell"><div><p className="eyebrow">Bangalore / The collection</p><h1 className="display-title">Places with<br /><em>a point of view.</em></h1></div><p className="collection-intro">A small, growing edit of homes, plots and spaces across the city. Take your time.</p></header><div className="collection-filter-bar section-shell"><span>08 places / 04 neighbourhoods</span><span>Curated September 2026 <ArrowRight size={14} /></span></div><section className="collection-grid section-shell">{properties.map((property, index) => <PropertyCard key={property.slug} property={property} featured={index === 0} />)}</section><footer className="collection-footer section-shell"><Link href="/" className="text-link"><ArrowLeft size={16} /> Back to the journal</Link><span>More places are on their way.</span></footer></main>;
}
