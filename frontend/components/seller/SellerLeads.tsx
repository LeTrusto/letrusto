"use client";

import { ArrowLeft, ArrowRight, CalendarDays, Mail, MapPin, Phone, RefreshCw, Send } from "lucide-react";
import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import SellerStatus, { statusLabel } from "@/components/seller/SellerStatus";
import { useAuth } from "@/hooks/useAuth";
import { getSellerEnquiry, listSellerEnquiries, updateSellerEnquiryStatus, type SellerEnquiry } from "@/services/seller.service";

const statuses = ["NEW", "CONTACTED", "FOLLOW_UP", "VISITED", "CLOSED"];

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value));
}

function formatBudget(value: number | string | null) {
  if (value == null) return "Not shared";
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(value));
}

function sourceLabel(enquiry: SellerEnquiry) {
  return [enquiry.source, enquiry.source_medium, enquiry.source_content].filter(Boolean).join(" -> ") || "Unknown";
}

function friendlyLeadError(error: unknown) {
  const message = error instanceof Error ? error.message : "";
  if (message.includes("401")) return "Please sign in to view your enquiries.";
  if (message.includes("403")) return "You don't have permission to view this enquiry.";
  if (message.includes("404")) return "We couldn't find this enquiry.";
  return "Something went wrong while loading your enquiries.";
}

export default function SellerLeads() {
  const { accessToken } = useAuth();
  const searchParams = useSearchParams();
  const propertyFilter = searchParams.get("property");
  const [enquiries, setEnquiries] = useState<SellerEnquiry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = async () => {
    if (!accessToken) return;
    setLoading(true);
    setError("");
    try { setEnquiries(await listSellerEnquiries(accessToken)); } catch (err) { setError(friendlyLeadError(err)); } finally { setLoading(false); }
  };
  useEffect(() => {
    let cancelled = false;
    if (!accessToken) return () => { cancelled = true; };
    void listSellerEnquiries(accessToken).then((loaded) => {
      if (!cancelled) setEnquiries(loaded);
    }).catch((err) => {
      if (!cancelled) setError(friendlyLeadError(err));
    }).finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => { cancelled = true; };
  }, [accessToken]);
  const visible = useMemo(() => propertyFilter ? enquiries.filter((enquiry) => enquiry.property_id === propertyFilter) : enquiries, [enquiries, propertyFilter]);
  const counts = enquiries.reduce<Record<string, number>>((result, enquiry) => { result[enquiry.status] = (result[enquiry.status] ?? 0) + 1; return result; }, {});
  const update = async (id: string, status: string) => {
    if (!accessToken) return;
    try { const updated = await updateSellerEnquiryStatus(accessToken, id, status); setEnquiries((current) => current.map((enquiry) => enquiry.id === id ? updated : enquiry)); } catch (err) { setError(friendlyLeadError(err)); }
  };
  return <><header className="seller-page-heading"><div><p className="eyebrow">Seller studio</p><h1 className="seller-display-title">Buyer enquiries</h1><p className="seller-muted">See who is interested in your properties and decide what happens next.</p></div><Link href="/seller" className="seller-secondary-button"><ArrowLeft size={16} /> My properties</Link></header>{error && <div className="seller-alert" role="alert">{error}<button type="button" onClick={() => void load()}><RefreshCw size={15} /> Try again</button></div>}<section className="lead-summary-grid" aria-label="Enquiry summary">{statuses.map((status) => <div key={status}><span>{statusLabel(status)}</span><strong>{counts[status] ?? 0}</strong></div>)}</section>{loading ? <p className="seller-empty">Loading your enquiries...</p> : visible.length === 0 ? <div className="seller-empty seller-empty-panel"><p className="eyebrow">The next conversation</p><h2>No buyer enquiries yet</h2><p>When buyers enquire about your live properties, you&apos;ll see them here.</p><Link href="/seller" className="seller-primary-button">View my properties <ArrowRight size={16} /></Link></div> : <section className="lead-list" aria-label="Buyer enquiries">{visible.map((enquiry) => <LeadCard key={enquiry.id} enquiry={enquiry} onStatusChange={update} />)}</section>}</>;
}

function LeadCard({ enquiry, onStatusChange }: { enquiry: SellerEnquiry; onStatusChange: (id: string, status: string) => Promise<void> }) {
  return <article className="lead-card"><div className="lead-card-main"><div className="lead-card-heading"><div><p className="seller-card-kicker">New enquiry · {formatDate(enquiry.created_at)}</p><h2>{enquiry.buyer_name}</h2></div><SellerStatus status={enquiry.status} /></div><Link className="lead-property" href={`/seller/properties/${enquiry.property_id}`}><strong>{enquiry.property_title}</strong><span><MapPin size={14} /> {enquiry.locality}, Bengaluru</span><ArrowRight size={16} /></Link><div className="lead-facts"><span><strong>Budget</strong>{formatBudget(enquiry.budget_amount)}</span><span><strong>Timeline</strong>{enquiry.buying_timeline || "Not shared"}</span><span><strong>Contact</strong>{statusLabel(enquiry.preferred_contact_method)}</span><span><strong>Source</strong>{sourceLabel(enquiry)}</span></div>{enquiry.message && <p className="lead-message">&ldquo;{enquiry.message}&rdquo;</p>}</div><div className="lead-card-actions"><label>Status<select aria-label={`Update status for ${enquiry.buyer_name}`} value={enquiry.status} onChange={(event) => void onStatusChange(enquiry.id, event.target.value)}>{statuses.map((status) => <option key={status} value={status}>{statusLabel(status)}</option>)}</select></label><div className="lead-contact-actions">{enquiry.buyer_phone && enquiry.consent_to_share && <a href={`tel:${enquiry.buyer_phone}`} aria-label={`Call ${enquiry.buyer_name}`}><Phone size={16} /> Call</a>}{enquiry.buyer_email && enquiry.consent_to_share && <a href={`mailto:${enquiry.buyer_email}`} aria-label={`Email ${enquiry.buyer_name}`}><Mail size={16} /> Email</a>}</div><Link className="lead-detail-link" href={`/seller/leads/${enquiry.id}`}>View enquiry <ArrowRight size={15} /></Link></div></article>;
}

export function SellerLeadDetail() {
  const { accessToken } = useAuth();
  const params = useParams<{ id: string }>();
  const [enquiry, setEnquiry] = useState<SellerEnquiry | null>(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  useEffect(() => { if (accessToken && params.id) void getSellerEnquiry(accessToken, params.id).then(setEnquiry).catch((err) => setError(friendlyLeadError(err))); }, [accessToken, params.id]);
  async function update(status: string) { if (!accessToken || !enquiry) return; setSaving(true); setError(""); try { setEnquiry(await updateSellerEnquiryStatus(accessToken, enquiry.id, status)); } catch (err) { setError(friendlyLeadError(err)); } finally { setSaving(false); } }
  if (error) return <div className="seller-empty seller-empty-panel"><p className="eyebrow">Enquiry unavailable</p><h1>{error}</h1><Link href="/seller/leads" className="seller-primary-button">Back to enquiries <ArrowLeft size={16} /></Link></div>;
  if (!enquiry) return <p className="seller-empty">Loading enquiry...</p>;
  return <><header className="seller-page-heading"><div><Link href="/seller/leads" className="seller-back-link"><ArrowLeft size={15} /> All enquiries</Link><p className="eyebrow">Buyer enquiry</p><h1 className="seller-display-title">{enquiry.buyer_name}</h1><p className="seller-muted">{enquiry.property_title} · {enquiry.locality}, Bengaluru</p></div><SellerStatus status={enquiry.status} /></header>{error && <p className="seller-alert" role="alert">{error}</p>}<div className="lead-detail-grid"><section className="seller-form-panel"><h2>What they shared</h2><div className="lead-detail-facts"><div><span>Property</span><strong>{enquiry.property_title}</strong><small>{enquiry.locality}, Bengaluru</small></div><div><span>Received</span><strong><CalendarDays size={15} /> {formatDate(enquiry.created_at)}</strong></div><div><span>Budget</span><strong>{formatBudget(enquiry.budget_amount)}</strong></div><div><span>Timeline</span><strong>{enquiry.buying_timeline || "Not shared"}</strong></div><div><span>Preferred contact</span><strong>{statusLabel(enquiry.preferred_contact_method)}</strong></div><div><span>Source</span><strong>{sourceLabel(enquiry)}</strong></div></div>{enquiry.message && <blockquote>{enquiry.message}</blockquote>}<Link href={`/seller/properties/${enquiry.property_id}`} className="seller-secondary-button">View property <ArrowRight size={16} /></Link></section><aside className="seller-form-panel lead-detail-actions"><h2>Next action</h2><label>Status<select aria-label="Update enquiry status" disabled={saving} value={enquiry.status} onChange={(event) => void update(event.target.value)}>{statuses.map((status) => <option key={status} value={status}>{statusLabel(status)}</option>)}</select></label>{enquiry.consent_to_share && (enquiry.buyer_phone || enquiry.buyer_email) && <div className="lead-contact-card"><p>Contact details</p>{enquiry.buyer_phone && <a href={`tel:${enquiry.buyer_phone}`}><Phone size={16} /> {enquiry.buyer_phone}</a>}{enquiry.buyer_email && <a href={`mailto:${enquiry.buyer_email}`}><Mail size={16} /> {enquiry.buyer_email}</a>}</div>}<h2>History</h2><div className="lead-history"><div><Send size={14} /><span>Enquiry received</span><small>{formatDate(enquiry.created_at)}</small></div>{enquiry.history.map((item) => <div key={`${item.created_at}-${item.new_status}`}><Send size={14} /><span>{statusLabel(item.new_status)}{item.note ? ` · ${item.note}` : ""}</span><small>{formatDate(item.created_at)}</small></div>)}</div></aside></div></>;
}
