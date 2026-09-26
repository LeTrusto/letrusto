"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { Check, X } from "lucide-react";

import { createPropertyEnquiry, type PublicProperty, validateEnquiry } from "@/services/property.service";

const initialForm = {
  buyer_name: "",
  buyer_phone: "",
  buyer_email: "",
  whatsapp_available: false,
  budget_amount: "",
  buying_timeline: "",
  message: "",
  preferred_contact_method: "PHONE" as const,
  consent_to_share: false,
};

type FormState = typeof initialForm;

function formatPrice(property: PublicProperty): string {
  const amount = Number(property.price_amount);
  if (!Number.isFinite(amount)) return `${property.currency} ${property.price_amount}`;
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: property.currency, maximumFractionDigits: 0 }).format(amount);
}

export function PropertyEnquiry({ property }: { property: PublicProperty }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<FormState>(initialForm);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const dialogRef = useRef<HTMLDivElement>(null);
  const firstFieldRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    firstFieldRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open]);

  function updateField<K extends keyof FormState>(field: K, value: FormState[K]) {
    setForm((current) => ({ ...current, [field]: value }));
    setErrors((current) => ({ ...current, [field]: "" }));
    if (status === "error") setStatus("idle");
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validation = validateEnquiry(form);
    setErrors(validation);
    if (Object.keys(validation).length > 0) return;

    setStatus("submitting");
    const attribution = new URLSearchParams(window.location.search);
    const source = attribution.get("utm_source")?.toUpperCase();
    const supportedSources = ["INSTAGRAM", "FACEBOOK", "WHATSAPP", "DIRECT", "QR", "OTHER"];
    createPropertyEnquiry(property.id, {
      buyer_name: form.buyer_name.trim(),
      buyer_phone: form.buyer_phone.trim(),
      buyer_email: form.buyer_email.trim() || undefined,
      whatsapp_available: form.whatsapp_available,
      budget_amount: form.budget_amount ? Number(form.budget_amount) : undefined,
      buying_timeline: form.buying_timeline || undefined,
      message: form.message.trim() || undefined,
      preferred_contact_method: form.preferred_contact_method,
      source: supportedSources.includes(source ?? "") ? source as "INSTAGRAM" | "FACEBOOK" | "WHATSAPP" | "DIRECT" | "QR" | "OTHER" : "WEBSITE",
      source_medium: attribution.get("utm_medium") || undefined,
      source_content: attribution.get("utm_content") || undefined,
      landing_path: `${window.location.pathname}${window.location.search}`,
      consent_to_share: form.consent_to_share,
    }).then(() => setStatus("success")).catch(() => setStatus("error"));
  }

  return (
    <>
      <div className="property-enquiry-cta">
        <div><p className="eyebrow">Ready to take the next step?</p><p>Contact the owner to ask questions, discuss the negotiable price, or arrange a visit.</p></div>
        <button type="button" className="button button-dark" onClick={() => { setOpen(true); setStatus("idle"); }}>Contact owner</button>
      </div>
      {open && <div className="enquiry-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false); }}>
        <div className="enquiry-dialog" role="dialog" aria-modal="true" aria-labelledby="enquiry-title" ref={dialogRef}>
          <button type="button" className="enquiry-close" aria-label="Close enquiry form" onClick={() => setOpen(false)}><X size={18} /></button>
          {status === "success" ? (
            <div className="enquiry-success" role="status">
              <span className="success-mark"><Check size={22} /></span>
              <p className="eyebrow">Enquiry received</p>
              <h2 id="enquiry-title">Your enquiry has been sent.</h2>
              <p>Thanks for your interest. The property contact can now follow up with you.</p>
              <div className="enquiry-summary"><strong>{property.title}</strong><span>{property.location.name}, Bengaluru · {formatPrice(property)}</span></div>
              <button type="button" className="button button-dark" onClick={() => setOpen(false)}>Back to property</button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} noValidate>
              <p className="eyebrow">Contact the owner</p>
              <h2 id="enquiry-title">Make your interest known.</h2>
              <p className="enquiry-intro">Share your details and the authorized property contact can respond about the price, availability, or a visit.</p>
              <div className="enquiry-fields">
                <label>Name <input ref={firstFieldRef} value={form.buyer_name} onChange={(event) => updateField("buyer_name", event.target.value)} placeholder="Your full name" aria-invalid={Boolean(errors.buyer_name)} />{errors.buyer_name && <span className="field-error">{errors.buyer_name}</span>}</label>
                <label>Phone <input type="tel" value={form.buyer_phone} onChange={(event) => updateField("buyer_phone", event.target.value)} placeholder="10-digit phone number" aria-invalid={Boolean(errors.buyer_phone)} />{errors.buyer_phone && <span className="field-error">{errors.buyer_phone}</span>}</label>
                <label>Email <input type="email" value={form.buyer_email} onChange={(event) => updateField("buyer_email", event.target.value)} placeholder="Optional email address" /></label>
                <label>Budget <input type="number" min="0" value={form.budget_amount} onChange={(event) => updateField("budget_amount", event.target.value)} placeholder="Optional budget in INR" /></label>
                <label>Buying timeline <select value={form.buying_timeline} onChange={(event) => updateField("buying_timeline", event.target.value)}><option value="">Choose if you know</option><option value="IMMEDIATE">Immediately</option><option value="THREE_MONTHS">Within 3 months</option><option value="SIX_MONTHS">Within 6 months</option><option value="EXPLORING">Just exploring</option></select></label>
                <label>Preferred contact <select value={form.preferred_contact_method} onChange={(event) => updateField("preferred_contact_method", event.target.value as FormState["preferred_contact_method"])}><option value="PHONE">Phone</option><option value="WHATSAPP">WhatsApp</option><option value="EMAIL">Email</option></select></label>
                <label className="enquiry-wide">Message <textarea value={form.message} onChange={(event) => updateField("message", event.target.value)} placeholder="What would you like to know?" rows={3} /></label>
              </div>
              <label className="consent-check"><input type="checkbox" checked={form.whatsapp_available} onChange={(event) => updateField("whatsapp_available", event.target.checked)} /> WhatsApp is available on this number.</label>
              <label className="consent-check"><input type="checkbox" checked={form.consent_to_share} onChange={(event) => updateField("consent_to_share", event.target.checked)} aria-invalid={Boolean(errors.consent_to_share)} /> <span>I agree to share my contact details with the seller/authorized property contact for this enquiry.</span></label>
              {errors.consent_to_share && <span className="field-error consent-error">{errors.consent_to_share}</span>}
              {status === "error" && <div className="enquiry-error" role="alert">Something went wrong while sending your enquiry. Please try again.</div>}
              <button type="submit" className="button button-dark enquiry-submit" disabled={status === "submitting"}>{status === "submitting" ? "Sending..." : "Send enquiry"}</button>
            </form>
          )}
        </div>
      </div>}
    </>
  );
}
