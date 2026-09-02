"use client";

import { Loader2, Send } from "lucide-react";
import { useState } from "react";
import { buildApiUrl, IS_API_CONFIGURED } from "@/services/api";
import type { Service } from "@/types/services";

type QuoteFormProps = { services: Service[]; initialServiceSlug?: string };
type FormState = { name: string; email: string; phone: string; serviceSlug: string; description: string; website: string; requirements: string; timeline: string; budget: string };
const emptyForm = (serviceSlug: string): FormState => ({ name: "", email: "", phone: "", serviceSlug, description: "", website: "", requirements: "", timeline: "", budget: "" });

export default function QuoteForm({ services, initialServiceSlug }: QuoteFormProps) {
  const selectedInitial = services.some((service) => service.slug === initialServiceSlug) ? initialServiceSlug ?? services[0]?.slug ?? "" : services[0]?.slug ?? "";
  const [form, setForm] = useState<FormState>(() => emptyForm(selectedInitial));
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  function update(field: keyof FormState, value: string) { setForm((current) => ({ ...current, [field]: value })); }
  function validate() {
    if (!form.name.trim() || form.name.trim().length < 2) return "Enter your name.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return "Enter a valid email address.";
    if (form.phone && !/^[+\d][\d\s().-]{6,28}$/.test(form.phone)) return "Enter a valid phone or WhatsApp number.";
    if (!services.some((service) => service.slug === form.serviceSlug)) return "Choose a service.";
    if (form.description.trim().length < 20) return "Tell us a little more about the project (at least 20 characters).";
    if (form.description.length > 1000 || form.requirements.length > 400) return "Please keep the project details within the stated limits.";
    return "";
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const validationError = validate();
    setError(validationError);
    if (validationError || !IS_API_CONFIGURED) return;
    setSubmitting(true);
    try {
      const service = services.find((item) => item.slug === form.serviceSlug);
      const details = [`Service: ${service?.name ?? form.serviceSlug}`, `Name: ${form.name.trim()}`, `Phone/WhatsApp: ${form.phone.trim() || "Not provided"}`, `Project description: ${form.description.trim()}`, `Current website: ${form.website.trim() || "Not provided"}`, `Approximate requirements: ${form.requirements.trim() || "Not provided"}`, `Preferred timeline: ${form.timeline || "Not provided"}`, `Budget range: ${form.budget || "Not provided"}`].join("\n");
      const response = await fetch(buildApiUrl("/support/tickets"), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: form.email.trim(), category: "service_enquiry", subject: `Service enquiry: ${service?.name ?? form.serviceSlug}`, body: details, service_slug: form.serviceSlug, customer_name: form.name.trim(), phone: form.phone.trim() || null, current_website: form.website.trim() || null, timeline: form.timeline || null, budget_range: form.budget || null }) });
      const payload = (await response.json().catch(() => ({}))) as { detail?: string; message?: string };
      if (!response.ok) throw new Error(payload.detail ?? "We could not submit your enquiry right now.");
      setSubmitted(true);
    } catch (submissionError) { setError(submissionError instanceof Error ? submissionError.message : "We could not submit your enquiry right now."); } finally { setSubmitting(false); }
  }

  if (submitted) return <div className="lt-card border-[var(--lt-success)]" role="status"><p className="lt-eyebrow">Enquiry received</p><h2 className="lt-heading-2 mt-3">Thanks, {form.name.trim()}.</h2><p className="mt-4 text-sm leading-6 text-[var(--text-secondary)]">Your enquiry about {services.find((service) => service.slug === form.serviceSlug)?.name ?? "this service"} has been sent to LeTrusto. We will review the details and follow up using {form.email}.</p><button type="button" className="lt-btn lt-btn-sm lt-btn-secondary mt-6" onClick={() => { setSubmitted(false); setForm(emptyForm(form.serviceSlug)); }}>Send another enquiry</button></div>;

  return <form onSubmit={(event) => { void submit(event); }} className="lt-card space-y-6" noValidate><div><p className="lt-eyebrow">Project enquiry</p><h2 className="lt-heading-2 mt-2">Tell us what you need</h2><p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">Share enough context for a useful first conversation. No account is required and a quote is not generated automatically.</p></div>{error && <p className="border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700" role="alert">{error}</p>}<div className="grid gap-5 sm:grid-cols-2"><Field label="Name" id="quote-name" value={form.name} onChange={(value) => update("name", value)} required placeholder="Your name" /><Field label="Email" id="quote-email" type="email" value={form.email} onChange={(value) => update("email", value)} required placeholder="you@example.com" /><Field label="Phone / WhatsApp" id="quote-phone" value={form.phone} onChange={(value) => update("phone", value)} placeholder="Optional" /><div><label htmlFor="quote-service" className="lt-label mb-2 block">Service interested in</label><select id="quote-service" className="lt-select w-full" value={form.serviceSlug} onChange={(event) => update("serviceSlug", event.target.value)} required>{services.map((service) => <option key={service.slug} value={service.slug}>{service.name}</option>)}</select></div></div><div><label htmlFor="quote-description" className="lt-label mb-2 block">Business or project description</label><textarea id="quote-description" className="lt-input min-h-28" value={form.description} onChange={(event) => update("description", event.target.value)} placeholder="What are you trying to build, improve or automate?" maxLength={1000} required /><p className="mt-1 text-xs text-[var(--text-muted)]">At least 20 characters.</p></div><div className="grid gap-5 sm:grid-cols-2"><Field label="Current website" id="quote-website" type="url" value={form.website} onChange={(value) => update("website", value)} placeholder="https://example.com (optional)" /><div><label htmlFor="quote-timeline" className="lt-label mb-2 block">Preferred timeline</label><select id="quote-timeline" className="lt-select w-full" value={form.timeline} onChange={(event) => update("timeline", event.target.value)}><option value="">Select (optional)</option><option>As soon as practical</option><option>This month</option><option>This quarter</option><option>Just exploring</option></select></div></div><div className="grid gap-5 sm:grid-cols-2"><div><label htmlFor="quote-requirements" className="lt-label mb-2 block">Approximate requirements</label><textarea id="quote-requirements" className="lt-input min-h-24" value={form.requirements} onChange={(event) => update("requirements", event.target.value)} placeholder="Pages, integrations, users or other useful details" maxLength={400} /></div><div><label htmlFor="quote-budget" className="lt-label mb-2 block">Budget range (optional)</label><select id="quote-budget" className="lt-select w-full" value={form.budget} onChange={(event) => update("budget", event.target.value)}><option value="">Prefer not to say</option><option>Under INR 25,000</option><option>INR 25,000–75,000</option><option>INR 75,000–1,50,000</option><option>Above INR 1,50,000</option><option>Not decided</option></select></div></div><button type="submit" disabled={submitting || !IS_API_CONFIGURED} className="lt-btn lt-btn-lg lt-btn-primary w-full sm:w-auto">{submitting ? <Loader2 size={17} className="animate-spin" aria-hidden="true" /> : <Send size={17} aria-hidden="true" />}{submitting ? "Sending enquiry" : "Send enquiry"}</button>{!IS_API_CONFIGURED && <p className="text-xs text-[var(--text-muted)]">The enquiry service is not connected in this environment.</p>}<p className="text-xs leading-5 text-[var(--text-muted)]">Only the details needed to understand and respond to this enquiry are submitted.</p></form>;
}

function Field({ label, id, type = "text", value, onChange, required = false, placeholder }: { label: string; id: string; type?: string; value: string; onChange: (value: string) => void; required?: boolean; placeholder: string }) { return <div><label htmlFor={id} className="lt-label mb-2 block">{label}{required && <span aria-hidden="true"> *</span>}</label><input id={id} type={type} className="lt-input" value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} required={required} /></div>; }