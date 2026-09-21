"use client";

import { ArrowRight, Plus, RefreshCw } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { listSellerEnquiries, listSellerProperties, type SellerEnquiry, type SellerProperty } from "@/services/seller.service";
import SellerStatus from "@/components/seller/SellerStatus";
import { useAuth } from "@/hooks/useAuth";

const typeLabels: Record<string, string> = { APARTMENT: "Apartment", INDEPENDENT_HOUSE: "Independent house", VILLA: "Villa", RESIDENTIAL_PLOT: "Residential plot" };

export default function SellerDashboard() {
  const { accessToken } = useAuth();
  const [properties, setProperties] = useState<SellerProperty[]>([]);
  const [enquiries, setEnquiries] = useState<SellerEnquiry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true); setError("");
    try { const [nextProperties, nextEnquiries] = await Promise.all([listSellerProperties(accessToken), listSellerEnquiries(accessToken)]); setProperties(nextProperties); setEnquiries(nextEnquiries); } catch { setError("We couldn't load your seller studio. Please try again."); } finally { setLoading(false); }
  }, [accessToken]);
  useEffect(() => {
    if (!accessToken) return;
    void Promise.resolve().then(() => load());
  }, [accessToken, load]);

  const counts = properties.reduce<Record<string, number>>((result, property) => { result[property.status] = (result[property.status] ?? 0) + 1; return result; }, {});
  const leadCounts = enquiries.reduce<Record<string, number>>((result, enquiry) => { result[enquiry.status] = (result[enquiry.status] ?? 0) + 1; return result; }, {});
  return <><header className="seller-page-heading"><div><p className="eyebrow">Seller studio</p><h1 className="seller-display-title">Your properties</h1><p className="seller-muted">A quiet place to shape your listings before they meet the city.</p></div><Link href="/seller/properties/new" className="seller-primary-button"><Plus size={17} /> Add property</Link></header><section className="seller-summary-grid" aria-label="Property summary"><div><span>Total properties</span><strong>{properties.length}</strong></div><div><span>Draft</span><strong>{counts.DRAFT ?? 0}</strong></div><div><span>Under review</span><strong>{(counts.SUBMITTED ?? 0) + (counts.UNDER_REVIEW ?? 0)}</strong></div><div><span>Live</span><strong>{counts.LIVE ?? 0}</strong></div></section><section className="seller-lead-summary" aria-label="Buyer enquiry summary"><div><p className="seller-section-label">Your leads</p><h2>{enquiries.length} buyer enquiries</h2><p>{enquiries.length ? `${leadCounts.NEW ?? 0} new · ${leadCounts.CONTACTED ?? 0} contacted · ${leadCounts.FOLLOW_UP ?? 0} follow-up · ${leadCounts.VISITED ?? 0} visited · ${leadCounts.CLOSED ?? 0} closed` : "Your buyer enquiries will appear here."}</p></div><Link href="/seller/leads" className="seller-secondary-button">View all leads <ArrowRight size={16} /></Link></section>{error && <div className="seller-alert" role="alert">{error}<button type="button" onClick={() => void load()}><RefreshCw size={15} /> Try again</button></div>}{loading ? <p className="seller-empty">Loading your properties...</p> : properties.length === 0 ? <div className="seller-empty seller-empty-panel"><p className="eyebrow">The first address</p><h2>Nothing here yet.</h2><p>Start with the details you know. You can save the rest for later.</p><Link href="/seller/properties/new" className="seller-primary-button">Add your first property <ArrowRight size={16} /></Link></div> : <section className="seller-property-list" aria-label="Your properties">{properties.map((property) => <SellerPropertyCard key={property.id} property={property} />)}</section>}</>;
}

function SellerPropertyCard({ property }: { property: SellerProperty }) {
  const cover = property.media.find((media) => media.is_cover)?.public_url ?? property.media.find((media) => media.public_url)?.public_url;
  return <article className="seller-property-card"><div className="seller-property-image">{cover ? <Image src={cover} alt="" fill unoptimized sizes="250px" /> : <span><span className="mark-dot" />No cover image yet</span>}</div><div className="seller-property-card-body"><div className="seller-property-card-top"><div><p className="seller-card-kicker">{typeLabels[property.property_type] ?? property.property_type} · {property.location.name}</p><h2>{property.title || "Untitled property"}</h2></div><SellerStatus status={property.status} /></div><p className="seller-property-price">{formatPrice(property.price_amount)}</p><p className="seller-card-meta">Last updated {formatDate(property.updated_at ?? property.created_at)}</p><Link href={`/seller/properties/${property.id}`} className="seller-card-link">Manage property <ArrowRight size={15} /></Link></div></article>;
}

function formatPrice(value: number | string) { return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(value)); }
function formatDate(value?: string) { return value ? new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value)) : "recently"; }
