import Link from "next/link";
import { ArrowLeft, ArrowRight, ShieldCheck } from "lucide-react";

import type { PublicProperty } from "@/services/property.service";
import { PropertyEnquiry } from "./PropertyEnquiry";
import { PropertyGallery } from "./PropertyGallery";

function formatPrice(property: PublicProperty): string {
  const amount = Number(property.price_amount);
  if (!Number.isFinite(amount)) return `${property.currency} ${property.price_amount}`;
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: property.currency, maximumFractionDigits: 0 }).format(amount);
}

function numberLabel(value: number | string | null, suffix: string): string | null {
  if (value === null || value === "") return null;
  return `${Number(value).toLocaleString("en-IN")} ${suffix}`;
}

function typeLabel(type: string): string {
  return type.replaceAll("_", " ").toLowerCase().replace(/(^| )\w/g, (letter) => letter.toUpperCase());
}

function verificationLabel(label: string): string {
  if (label === "DOCUMENT_EVIDENCE_REVIEWED") return "Document evidence reviewed";
  if (label === "RELATIONSHIP_REVIEWED") return "Relationship reviewed";
  if (label === "CONTACT_VERIFIED") return "Contact verified";
  return "Verification in progress";
}

export function PropertyUnavailable() {
  return <main className="property-unavailable section-shell"><p className="eyebrow">Bangalore / Property journal</p><h1 className="display-title">This property is<br /><em>no longer available.</em></h1><p>Explore other properties across Bengaluru and find the place that feels right.</p><Link href="/properties" className="button button-dark">Explore properties <ArrowRight size={17} /></Link></main>;
}

export function PropertyDetail({ property }: { property: PublicProperty }) {
  const facts = [
    property.bhk !== null ? { label: "Bedrooms", value: `${property.bhk} BHK` } : null,
    numberLabel(property.built_up_area_sqft, "sq.ft built-up") ? { label: "Built-up", value: numberLabel(property.built_up_area_sqft, "sq.ft built-up")! } : null,
    numberLabel(property.carpet_area_sqft, "sq.ft carpet") ? { label: "Carpet area", value: numberLabel(property.carpet_area_sqft, "sq.ft carpet")! } : null,
    numberLabel(property.plot_area_sqft, "sq.ft plot") ? { label: "Plot area", value: numberLabel(property.plot_area_sqft, "sq.ft plot")! } : null,
    property.floor_number !== null ? { label: "Floor", value: property.total_floors ? `${property.floor_number} of ${property.total_floors}` : `${property.floor_number}` } : null,
    property.parking_details ? { label: "Parking", value: property.parking_details } : null,
    property.facing ? { label: "Facing", value: property.facing } : null,
    property.possession_status ? { label: "Possession", value: property.possession_status } : null,
    property.maintenance_amount ? { label: "Maintenance", value: `₹${Number(property.maintenance_amount).toLocaleString("en-IN")}` } : null,
  ].filter((fact): fact is { label: string; value: string } => Boolean(fact));

  return <main className="property-detail-page">
    <nav className="site-nav detail-nav section-shell" aria-label="Property navigation"><Link href="/properties" className="temporary-mark"><span className="mark-dot" />BENGALURU PROPERTY</Link><div className="nav-links"><Link href="/">Journal</Link><Link href="/properties">The collection</Link><Link href="/login">For sellers</Link></div><Link href="/properties" className="nav-pill"><ArrowLeft size={15} /> Collection</Link></nav>
    <div className="property-detail-shell section-shell">
      <Link href="/properties" className="back-link"><ArrowLeft size={15} /> Back to the collection</Link>
      <PropertyGallery title={property.title} media={property.media} />
      <section className="detail-heading"><div><p className="eyebrow">{property.location.name} / {property.location.city_name}</p><h1>{property.title}</h1><p className="detail-type">{typeLabel(property.property_type)} · For sale</p></div><div className="detail-price"><span>Guide price</span><strong>{formatPrice(property)}</strong></div></section>
      <div className="detail-content-grid"><div className="detail-main-column"><section className="detail-facts" aria-label="Property facts">{facts.map((fact) => <div key={fact.label}><span>{fact.label}</span><strong>{fact.value}</strong></div>)}</section><section className="detail-copy"><p className="eyebrow">The story</p><h2>A place with room for a life.</h2><p>{property.description}</p></section><section className="detail-information"><p className="eyebrow">Property information</p><div className="information-list"><div><span>Location</span><strong>{property.location.name}, {property.location.city_name}</strong></div><div><span>Listing type</span><strong>{typeLabel(property.property_type)} · For sale</strong></div>{property.corner_site !== null && <div><span>Corner site</span><strong>{property.corner_site ? "Yes" : "No"}</strong></div>}{property.plot_dimensions && <div><span>Plot dimensions</span><strong>{property.plot_dimensions}</strong></div>}</div></section></div><aside className="detail-aside"><div className="verification-note"><ShieldCheck size={19} /><div><strong>{verificationLabel(property.verification_label)}</strong><p>Public information shown here is provided through the property listing.</p></div></div><PropertyEnquiry property={property} /></aside></div>
    </div>
  </main>;
}
