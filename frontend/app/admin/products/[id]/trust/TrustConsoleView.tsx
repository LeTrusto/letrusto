"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { ArrowLeft, CheckCircle2, Lock, Plus, ShieldCheck } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const VERIFICATION_STATUSES = ["PENDING", "VERIFIED", "REJECTED"] as const;

type Status = "UNVERIFIED" | "PENDING" | "VERIFIED" | "REJECTED" | "EXPIRED";
type Product = { id: string; name: string };
type Evidence = {
  id: string;
  evidence_type: string;
  title: string;
  description: string | null;
  source: string | null;
  reference_url: string | null;
  storage_reference: string | null;
  issued_at: string | null;
  expires_at: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};
type EvidenceLink = { id: string; evidence_id: string; created_at: string; evidence: Evidence };
type Claim = {
  id: string;
  product_id: string;
  claim_type: string;
  claim_value: string;
  claim_description: string | null;
  source: string | null;
  verification_status: Status;
  confidence: number | null;
  created_at: string;
  updated_at: string;
  evidence_links: EvidenceLink[];
};
type Verification = {
  id: string;
  claim_id: string;
  verification_status: Status;
  verification_method: string;
  notes: string | null;
  evidence_snapshot: Array<Record<string, unknown>> | null;
  verified_by_user_id: string | null;
  verified_at: string;
  expires_at: string | null;
};
type AuditEvent = {
  id: string;
  claim_id: string;
  evidence_id: string | null;
  verification_id: string | null;
  event_type: string;
  actor_user_id: string | null;
  previous_state: Record<string, unknown> | null;
  current_state: Record<string, unknown> | null;
  reason: string | null;
  event_metadata: Record<string, unknown> | null;
  created_at: string;
};
type ClaimDetail = Claim & { verifications: Verification[]; audit_events: AuditEvent[] };
type EvidenceFormState = { evidence_type: string; title: string; description: string; source: string; reference_url: string; storage_reference: string; issued_at: string; expires_at: string };
type TrustOptions = { claim_statuses: Status[]; verification_methods: string[] };

function headers(token: string | null, json = false): Record<string, string> {
  return { ...(json ? { "Content-Type": "application/json" } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) };
}

async function apiError(response: Response): Promise<string> {
  const body = (await response.json().catch(() => null)) as { detail?: string | Array<{ msg: string }> } | null;
  if (typeof body?.detail === "string") return body.detail;
  if (Array.isArray(body?.detail)) return body.detail.map((item) => item.msg).join("; ");
  if (response.status === 401) return "Your admin session has expired. Please sign in again.";
  if (response.status === 403) return "Admin access is required for Trust management.";
  if (response.status === 404) return "The requested product, claim, or evidence was not found.";
  return "The Trust request could not be completed.";
}

async function apiRequest<T>(token: string | null, path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}/api/v1/admin${path}`, { ...init, headers: { ...headers(token, Boolean(init?.body)), ...(init?.headers ?? {}) } });
  if (!response.ok) throw new Error(await apiError(response));
  return (await response.json()) as T;
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString("en-IN") : "-";
}

function StatusBadge({ status }: { status: Status }) {
  const styles: Record<Status, string> = {
    VERIFIED: "bg-green-100 text-green-800",
    PENDING: "bg-amber-100 text-amber-900",
    REJECTED: "bg-red-100 text-red-800",
    EXPIRED: "bg-slate-200 text-slate-700",
    UNVERIFIED: "bg-slate-100 text-slate-700",
  };
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${styles[status]}`}>{status}</span>;
}

export default function TrustConsoleView() {
  const { accessToken, isLoading: authLoading, isAuthenticated, isAdmin } = useAuth();
  const params = useParams<{ id: string }>();
  const productId = params.id;
  const [product, setProduct] = useState<Product | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [trustOptions, setTrustOptions] = useState<TrustOptions | null>(null);
  const [selectedClaim, setSelectedClaim] = useState<ClaimDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [showClaimForm, setShowClaimForm] = useState(false);
  const [showEvidenceForm, setShowEvidenceForm] = useState(false);
  const [editingClaim, setEditingClaim] = useState(false);
  const [verificationOpen, setVerificationOpen] = useState(false);
  const [claimForm, setClaimForm] = useState({ claim_type: "", claim_value: "", claim_description: "", source: "", confidence: "" });
  const [evidenceForm, setEvidenceForm] = useState<EvidenceFormState>({ evidence_type: "", title: "", description: "", source: "", reference_url: "", storage_reference: "", issued_at: "", expires_at: "" });
  const [verificationForm, setVerificationForm] = useState({ verification_status: "VERIFIED" as (typeof VERIFICATION_STATUSES)[number], verification_method: "", notes: "", expires_at: "", confirm: false });

  async function loadClaims() {
    const data = await apiRequest<Claim[]>(accessToken, `/trust/products/${productId}/claims`);
    setClaims(data);
    if (selectedClaim) {
      const detail = await apiRequest<ClaimDetail>(accessToken, `/trust/claims/${selectedClaim.id}`);
      setSelectedClaim(detail);
    }
  }

  useEffect(() => {
    if (!accessToken || !isAdmin || !productId) return;
    void Promise.resolve().then(() => setLoading(true));
    Promise.all([apiRequest<Product>(accessToken, `/products/${productId}`), apiRequest<Claim[]>(accessToken, `/trust/products/${productId}/claims`), apiRequest<TrustOptions>(accessToken, "/trust/options")]).then(([loadedProduct, loadedClaims, loadedOptions]) => {
      setProduct(loadedProduct);
      setClaims(loadedClaims);
      setTrustOptions(loadedOptions);
      setSelectedClaim(null);
    }).catch((err: unknown) => setError(err instanceof Error ? err.message : "Unable to load Trust data")).finally(() => setLoading(false));
  }, [accessToken, isAdmin, productId]);

  const counts = useMemo(() => claims.reduce<Record<Status, number>>((result, claim) => {
    result[claim.verification_status] += 1;
    return result;
  }, { VERIFIED: 0, PENDING: 0, REJECTED: 0, EXPIRED: 0, UNVERIFIED: 0 }), [claims]);

  async function selectClaim(claim: Claim) {
    setError("");
    try {
      setSelectedClaim(await apiRequest<ClaimDetail>(accessToken, `/trust/claims/${claim.id}`));
      setEditingClaim(false);
      setVerificationOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load claim details");
    }
  }

  async function submitClaim(event: FormEvent) {
    event.preventDefault();
    setWorking("claim"); setError(""); setMessage("");
    try {
      await apiRequest<Claim>(accessToken, "/trust/claims", { method: "POST", body: JSON.stringify({ product_id: productId, claim_type: claimForm.claim_type.trim(), claim_value: claimForm.claim_value.trim(), claim_description: claimForm.claim_description.trim() || null, source: claimForm.source.trim() || null, confidence: claimForm.confidence ? Number(claimForm.confidence) : null }) });
      setClaimForm({ claim_type: "", claim_value: "", claim_description: "", source: "", confidence: "" });
      setShowClaimForm(false); await loadClaims(); setMessage("Trust claim created.");
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to create claim"); } finally { setWorking(""); }
  }

  async function updateClaim(event: FormEvent) {
    event.preventDefault();
    if (!selectedClaim) return;
    setWorking("claim"); setError("");
    try {
      const updated = await apiRequest<Claim>(accessToken, `/trust/claims/${selectedClaim.id}`, { method: "PATCH", body: JSON.stringify({ claim_type: claimForm.claim_type.trim(), claim_value: claimForm.claim_value.trim(), claim_description: claimForm.claim_description.trim() || null, source: claimForm.source.trim() || null, confidence: claimForm.confidence ? Number(claimForm.confidence) : null }) });
      setClaims((current) => current.map((claim) => claim.id === updated.id ? updated : claim));
      setSelectedClaim({ ...selectedClaim, ...updated }); setEditingClaim(false); setMessage("Trust claim updated.");
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to update claim"); } finally { setWorking(""); }
  }

  function beginEdit() {
    if (!selectedClaim || selectedClaim.verification_status === "VERIFIED") return;
    setClaimForm({ claim_type: selectedClaim.claim_type, claim_value: selectedClaim.claim_value, claim_description: selectedClaim.claim_description ?? "", source: selectedClaim.source ?? "", confidence: selectedClaim.confidence == null ? "" : String(selectedClaim.confidence) });
    setEditingClaim(true);
  }

  async function createEvidence(event: FormEvent) {
    event.preventDefault();
    if (!selectedClaim) return;
    setWorking("evidence"); setError(""); setMessage("");
    try {
      const evidence = await apiRequest<Evidence>(accessToken, "/trust/evidence", { method: "POST", body: JSON.stringify({ evidence_type: evidenceForm.evidence_type.trim(), title: evidenceForm.title.trim(), description: evidenceForm.description.trim() || null, source: evidenceForm.source.trim() || null, reference_url: evidenceForm.reference_url.trim() || null, storage_reference: evidenceForm.storage_reference.trim() || null, issued_at: evidenceForm.issued_at ? new Date(evidenceForm.issued_at).toISOString() : null, expires_at: evidenceForm.expires_at ? new Date(evidenceForm.expires_at).toISOString() : null }) });
      await apiRequest(accessToken, `/trust/claims/${selectedClaim.id}/evidence`, { method: "POST", body: JSON.stringify({ evidence_id: evidence.id }) });
      setEvidenceForm({ evidence_type: "", title: "", description: "", source: "", reference_url: "", storage_reference: "", issued_at: "", expires_at: "" });
      setShowEvidenceForm(false); await selectClaim({ ...selectedClaim, ...evidence } as unknown as Claim); await loadClaims(); setMessage("Evidence created and attached.");
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to create and attach evidence"); } finally { setWorking(""); }
  }

  async function toggleEvidence(evidence: Evidence) {
    setWorking(`evidence-${evidence.id}`); setError("");
    try { await apiRequest<Evidence>(accessToken, `/trust/evidence/${evidence.id}`, { method: "PATCH", body: JSON.stringify({ is_active: !evidence.is_active }) }); await selectClaim(selectedClaim as unknown as Claim); await loadClaims(); setMessage(evidence.is_active ? "Evidence deactivated." : "Evidence reactivated."); }
    catch (err) { setError(err instanceof Error ? err.message : "Unable to update evidence"); } finally { setWorking(""); }
  }

  async function submitVerification(event: FormEvent) {
    event.preventDefault();
    if (!selectedClaim) return;
    const activeEvidence = selectedClaim.evidence_links.filter((link) => link.evidence.is_active);
    if (verificationForm.verification_status === "VERIFIED" && activeEvidence.length === 0) { setError("Add active evidence before verifying this claim."); return; }
    if (!verificationForm.confirm) { setError("Explicit confirmation is required before submitting verification."); return; }
    setWorking("verification"); setError(""); setMessage("");
    try {
      await apiRequest<Verification>(accessToken, `/trust/claims/${selectedClaim.id}/verifications`, { method: "POST", body: JSON.stringify({ verification_status: verificationForm.verification_status, verification_method: verificationForm.verification_method, notes: verificationForm.notes.trim() || null, evidence_ids: activeEvidence.map((link) => link.evidence_id), expires_at: verificationForm.expires_at ? new Date(verificationForm.expires_at).toISOString() : null }) });
      setVerificationOpen(false); setVerificationForm({ verification_status: "VERIFIED", verification_method: "", notes: "", expires_at: "", confirm: false }); await loadClaims(); if (selectedClaim) setSelectedClaim(await apiRequest<ClaimDetail>(accessToken, `/trust/claims/${selectedClaim.id}`)); setMessage("Verification submitted and history refreshed.");
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to submit verification"); } finally { setWorking(""); }
  }

  if (authLoading) return <main className="mx-auto max-w-5xl px-5 py-16 text-center">Loading admin access...</main>;
  if (!isAuthenticated || !isAdmin) return <main className="mx-auto max-w-3xl px-5 py-16 text-center"><Lock className="mx-auto text-[var(--text-muted)]" /><h1 className="lt-heading-2 mt-4">Admin access required</h1><Link href="/login" className="lt-btn lt-btn-primary mt-6 inline-flex">Sign In</Link></main>;
  if (loading) return <main className="mx-auto max-w-7xl px-5 py-10 text-sm text-[var(--text-muted)]">Loading Trust Console...</main>;
  if (!product) return <main className="mx-auto max-w-3xl px-5 py-16 text-center"><h1 className="lt-heading-2">Product not found</h1><Link href="/admin/products" className="lt-btn lt-btn-secondary mt-6 inline-flex">Back to Products</Link></main>;

  return <main className="mx-auto max-w-7xl px-5 py-8">
    <Link href="/admin/products" className="inline-flex items-center gap-2 text-sm font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)]"><ArrowLeft size={16} aria-hidden="true" /> Products</Link>
    <header className="mt-5 flex flex-col gap-4 border-b border-[var(--border)] pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div><p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">Internal Trust Console</p><h1 className="mt-1 text-2xl font-bold">{product.name}</h1><p className="mt-1 font-mono text-xs text-[var(--text-muted)]">Product ID: {product.id}</p></div>
      <div className="flex items-center gap-2"><ShieldCheck size={22} className="text-green-700" aria-hidden="true" /><span className="text-sm text-[var(--text-secondary)]">Evidence-backed product claims</span></div>
    </header>
    {error && <p role="alert" className="mt-4 border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</p>}
    {message && <p role="status" className="mt-4 border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">{message}</p>}
    <section className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-5">{(["VERIFIED", "PENDING", "REJECTED", "EXPIRED", "UNVERIFIED"] as Status[]).map((status) => <div key={status} className="lt-card p-4"><p className="text-xs uppercase text-[var(--text-muted)]">{status}</p><p className="mt-2 text-2xl font-bold">{counts[status]}</p></div>)}</section>
    <div className="mt-8 grid gap-8 xl:grid-cols-[minmax(0,1fr)_minmax(24rem,0.8fr)]">
      <section><div className="flex items-end justify-between gap-4"><div><h2 className="text-lg font-semibold">Trust Claims</h2><p className="mt-1 text-sm text-[var(--text-muted)]">Review what is being claimed and the evidence supporting it.</p></div><button type="button" onClick={() => { setShowClaimForm((value) => !value); setEditingClaim(false); }} className="lt-btn lt-btn-primary inline-flex items-center gap-2 text-sm"><Plus size={16} aria-hidden="true" /> Add Trust Claim</button></div>
        {showClaimForm && <ClaimForm form={claimForm} setForm={setClaimForm} onSubmit={submitClaim} working={working === "claim"} submitLabel="Create Claim" onCancel={() => setShowClaimForm(false)} />}
        {claims.length === 0 ? <div className="lt-card mt-5 p-8 text-center"><p className="font-semibold">No Trust claims have been added for this product yet.</p><button type="button" onClick={() => setShowClaimForm(true)} className="lt-btn lt-btn-secondary mt-4 text-sm">Add Trust Claim</button></div> : <div className="mt-5 space-y-3">{claims.map((claim) => <button type="button" key={claim.id} onClick={() => void selectClaim(claim)} className={`lt-card w-full p-4 text-left transition hover:border-slate-400 ${selectedClaim?.id === claim.id ? "border-slate-500" : ""}`}><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-xs font-semibold uppercase text-[var(--text-muted)]">{claim.claim_type}</p><p className="mt-1 font-semibold">{claim.claim_value}</p></div><StatusBadge status={claim.verification_status} /></div><div className="mt-4 grid grid-cols-2 gap-3 text-xs text-[var(--text-muted)] md:grid-cols-4"><span>Evidence <strong className="text-[var(--text-primary)]">{claim.evidence_links.length}</strong></span><span>Updated <strong className="text-[var(--text-primary)]">{formatDate(claim.updated_at)}</strong></span><span>Source <strong className="text-[var(--text-primary)]">{claim.source ?? "-"}</strong></span><span>Confidence <strong className="text-[var(--text-primary)]">{claim.confidence ?? "-"}</strong></span></div></button>)}</div>}
      </section>
      <section className="min-w-0">{selectedClaim ? <ClaimDetailPanel claim={selectedClaim} editing={editingClaim} form={claimForm} setForm={setClaimForm} onEdit={beginEdit} onCancelEdit={() => setEditingClaim(false)} onUpdate={updateClaim} working={working === "claim"} onAddEvidence={() => setShowEvidenceForm((value) => !value)} showEvidenceForm={showEvidenceForm} evidenceForm={evidenceForm} setEvidenceForm={setEvidenceForm} onCreateEvidence={createEvidence} evidenceWorking={working === "evidence"} onToggleEvidence={(evidence) => void toggleEvidence(evidence)} onVerify={() => setVerificationOpen((value) => !value)} verificationOpen={verificationOpen} verificationForm={verificationForm} setVerificationForm={setVerificationForm} verificationMethods={trustOptions?.verification_methods ?? []} onSubmitVerification={submitVerification} verificationWorking={working === "verification"} /> : <div className="lt-card p-8 text-center text-sm text-[var(--text-muted)]">Select a claim to review evidence, verification history, and audit events.</div>}</section>
    </div>
  </main>;
}

function ClaimForm({ form, setForm, onSubmit, working, submitLabel, onCancel }: { form: typeof initialClaimForm; setForm: (form: typeof initialClaimForm) => void; onSubmit: (event: FormEvent) => void; working: boolean; submitLabel: string; onCancel: () => void }) {
  return <form onSubmit={onSubmit} className="lt-card mt-4 grid gap-3 p-4 md:grid-cols-2"><Field label="Claim type" value={form.claim_type} required onChange={(value) => setForm({ ...form, claim_type: value })} /><Field label="Claim value" value={form.claim_value} required onChange={(value) => setForm({ ...form, claim_value: value })} /><Field label="Source" value={form.source} onChange={(value) => setForm({ ...form, source: value })} /><Field label="Confidence (0-100)" value={form.confidence} type="number" min="0" max="100" onChange={(value) => setForm({ ...form, confidence: value })} /><label className="text-xs text-[var(--text-muted)] md:col-span-2"><span>Description</span><textarea value={form.claim_description} onChange={(event) => setForm({ ...form, claim_description: event.target.value })} maxLength={10000} className="lt-input mt-1 min-h-20 w-full text-sm" /></label><div className="flex gap-2 md:col-span-2"><button type="submit" disabled={working || !form.claim_type.trim() || !form.claim_value.trim()} className="lt-btn lt-btn-primary text-sm">{working ? "Saving..." : submitLabel}</button><button type="button" onClick={onCancel} className="lt-btn lt-btn-secondary text-sm">Cancel</button></div></form>;
}

const initialClaimForm = { claim_type: "", claim_value: "", claim_description: "", source: "", confidence: "" };
function Field({ label, value, onChange, required = false, type = "text", min, max }: { label: string; value: string; onChange: (value: string) => void; required?: boolean; type?: string; min?: string; max?: string }) { return <label className="text-xs text-[var(--text-muted)]"><span>{label}</span><input required={required} type={type} min={min} max={max} value={value} onChange={(event) => onChange(event.target.value)} className="lt-input mt-1 w-full text-sm" /></label>; }

function ClaimDetailPanel({ claim, editing, form, setForm, onEdit, onCancelEdit, onUpdate, working, onAddEvidence, showEvidenceForm, evidenceForm, setEvidenceForm, onCreateEvidence, evidenceWorking, onToggleEvidence, onVerify, verificationOpen, verificationForm, setVerificationForm, verificationMethods, onSubmitVerification, verificationWorking }: { claim: ClaimDetail; editing: boolean; form: typeof initialClaimForm; setForm: (form: typeof initialClaimForm) => void; onEdit: () => void; onCancelEdit: () => void; onUpdate: (event: FormEvent) => void; working: boolean; onAddEvidence: () => void; showEvidenceForm: boolean; evidenceForm: EvidenceFormState; setEvidenceForm: (form: EvidenceFormState) => void; onCreateEvidence: (event: FormEvent) => void; evidenceWorking: boolean; onToggleEvidence: (evidence: Evidence) => void; onVerify: () => void; verificationOpen: boolean; verificationForm: { verification_status: (typeof VERIFICATION_STATUSES)[number]; verification_method: string; notes: string; expires_at: string; confirm: boolean }; setVerificationForm: (form: { verification_status: (typeof VERIFICATION_STATUSES)[number]; verification_method: string; notes: string; expires_at: string; confirm: boolean }) => void; verificationMethods: string[]; onSubmitVerification: (event: FormEvent) => void; verificationWorking: boolean }) {
  const activeEvidence = claim.evidence_links.filter((link) => link.evidence.is_active);
  return <div className="space-y-5"><div className="lt-card p-5"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-xs font-semibold uppercase text-[var(--text-muted)]">{claim.claim_type}</p><h2 className="mt-1 text-lg font-semibold">{claim.claim_value}</h2><p className="mt-2 text-sm text-[var(--text-secondary)]">{claim.claim_description ?? "No description provided."}</p></div><StatusBadge status={claim.verification_status} /></div>{claim.verification_status === "VERIFIED" ? <p className="mt-4 border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">Verified claims cannot be directly edited. Start a new verification workflow to update this claim.</p> : <button type="button" onClick={onEdit} className="lt-btn lt-btn-secondary mt-4 text-sm">Edit eligible claim</button>}{claim.verification_status === "EXPIRED" && <p className="mt-3 text-sm text-slate-700">This verification has expired. Start re-verification to establish a current result.</p>}{editing && <ClaimForm form={form} setForm={setForm} onSubmit={onUpdate} working={working} submitLabel="Save Claim" onCancel={onCancelEdit} />}</div>
    <section className="lt-card p-5"><div className="flex items-start justify-between gap-3"><div><h3 className="font-semibold">Evidence</h3><p className="mt-1 text-sm text-[var(--text-muted)]">{activeEvidence.length} active of {claim.evidence_links.length} attached</p></div><button type="button" onClick={onAddEvidence} className="lt-btn lt-btn-secondary inline-flex items-center gap-2 text-sm"><Plus size={16} aria-hidden="true" /> Add Evidence</button></div>{showEvidenceForm && <EvidenceForm form={evidenceForm} setForm={setEvidenceForm} onSubmit={onCreateEvidence} working={evidenceWorking} onCancel={onAddEvidence} />}{claim.evidence_links.length === 0 ? <p className="mt-5 text-sm text-[var(--text-muted)]">No evidence is attached to this claim yet.</p> : <div className="mt-5 space-y-3">{claim.evidence_links.map((link) => <div key={link.id} className="border-t border-[var(--border)] pt-3"><div className="flex items-start justify-between gap-3"><div><p className="font-semibold">{link.evidence.title}</p><p className="text-xs text-[var(--text-muted)]">{link.evidence.evidence_type} · {link.evidence.source ?? "Source not recorded"}</p></div><span className={`text-xs font-semibold ${link.evidence.is_active ? "text-green-700" : "text-slate-500"}`}>{link.evidence.is_active ? "ACTIVE" : "INACTIVE"}</span></div><p className="mt-1 text-sm">{link.evidence.description ?? "No description."}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Created {formatDate(link.evidence.created_at)} · Expires {formatDate(link.evidence.expires_at)}</p>{link.evidence.reference_url && <a href={link.evidence.reference_url} target="_blank" rel="noreferrer" className="mt-1 block truncate text-xs underline">{link.evidence.reference_url}</a>}<button type="button" disabled={evidenceWorking} onClick={() => onToggleEvidence(link.evidence)} className="lt-btn lt-btn-secondary mt-2 text-xs">{link.evidence.is_active ? "Deactivate" : "Reactivate"}</button></div>)}</div>}</section>
    <section className="lt-card p-5"><div className="flex items-start justify-between gap-3"><div><h3 className="font-semibold">Verification workflow</h3><p className="mt-1 text-sm text-[var(--text-muted)]">Review attached evidence before recording a new historical result.</p></div><button type="button" onClick={onVerify} className="lt-btn lt-btn-primary inline-flex items-center gap-2 text-sm"><CheckCircle2 size={16} aria-hidden="true" /> {claim.verification_status === "VERIFIED" || claim.verification_status === "EXPIRED" ? "Start Re-verification" : "Start Verification"}</button></div>{verificationOpen && <VerificationForm activeEvidence={activeEvidence} form={verificationForm} setForm={setVerificationForm} verificationMethods={verificationMethods} onSubmit={onSubmitVerification} working={verificationWorking} onCancel={onVerify} />}</section>
    <History title="Verification History" empty="This claim has not been verified yet.">{claim.verifications.map((item) => <div key={item.id} className="border-t border-[var(--border)] py-3"><div className="flex flex-wrap items-center gap-2"><StatusBadge status={item.verification_status} /><strong>{item.verification_method}</strong><span className="text-xs text-[var(--text-muted)]">{formatDate(item.verified_at)}</span></div><p className="mt-1 text-sm">{item.notes ?? "No reason or notes recorded."}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Verified by {item.verified_by_user_id ?? "-"} · Expires {formatDate(item.expires_at)} · Evidence snapshot {item.evidence_snapshot?.length ?? 0} item(s)</p></div>)}</History>
    <History title="Trust Audit History" empty="No audit events recorded.">{claim.audit_events.map((event) => <div key={event.id} className="border-t border-[var(--border)] py-3"><div className="flex flex-wrap items-center gap-2"><strong>{event.event_type.replaceAll("_", " ")}</strong><span className="text-xs text-[var(--text-muted)]">{formatDate(event.created_at)}</span></div><p className="mt-1 text-sm">{event.reason ?? "No reason recorded."}</p><p className="mt-1 text-xs text-[var(--text-muted)]">Actor {event.actor_user_id ?? "-"}</p></div>)}</History>
  </div>;
}

function EvidenceForm({ form, setForm, onSubmit, working, onCancel }: { form: EvidenceFormState; setForm: (form: EvidenceFormState) => void; onSubmit: (event: FormEvent) => void; working: boolean; onCancel: () => void }) { const update = (key: keyof EvidenceFormState, value: string) => setForm({ ...form, [key]: value }); return <form onSubmit={onSubmit} className="mt-4 grid gap-3 border-t border-[var(--border)] pt-4 md:grid-cols-2"><Field label="Evidence type" value={form.evidence_type} required onChange={(value) => update("evidence_type", value)} /><Field label="Title" value={form.title} required onChange={(value) => update("title", value)} /><Field label="Source" value={form.source} onChange={(value) => update("source", value)} /><Field label="Reference URL" value={form.reference_url} type="url" onChange={(value) => update("reference_url", value)} /><Field label="Storage reference" value={form.storage_reference} onChange={(value) => update("storage_reference", value)} /><Field label="Issue date" value={form.issued_at} type="datetime-local" onChange={(value) => update("issued_at", value)} /><Field label="Expiry date" value={form.expires_at} type="datetime-local" onChange={(value) => update("expires_at", value)} /><label className="text-xs text-[var(--text-muted)] md:col-span-2"><span>Description</span><textarea value={form.description} onChange={(event) => update("description", event.target.value)} className="lt-input mt-1 min-h-16 w-full text-sm" /></label><div className="flex gap-2 md:col-span-2"><button type="submit" disabled={working || (!form.reference_url.trim() && !form.storage_reference.trim()) || !form.evidence_type.trim() || !form.title.trim()} className="lt-btn lt-btn-primary text-sm">{working ? "Saving..." : "Create and Attach"}</button><button type="button" onClick={onCancel} className="lt-btn lt-btn-secondary text-sm">Cancel</button></div></form>; }

function VerificationForm({ activeEvidence, form, setForm, verificationMethods, onSubmit, working, onCancel }: { activeEvidence: EvidenceLink[]; form: { verification_status: (typeof VERIFICATION_STATUSES)[number]; verification_method: string; notes: string; expires_at: string; confirm: boolean }; setForm: (form: { verification_status: (typeof VERIFICATION_STATUSES)[number]; verification_method: string; notes: string; expires_at: string; confirm: boolean }) => void; verificationMethods: string[]; onSubmit: (event: FormEvent) => void; working: boolean; onCancel: () => void }) { return <form onSubmit={onSubmit} className="mt-4 space-y-4 border-t border-[var(--border)] pt-4"><div className="grid gap-3 md:grid-cols-2"><label className="text-xs text-[var(--text-muted)]"><span>Result</span><select value={form.verification_status} onChange={(event) => setForm({ ...form, verification_status: event.target.value as (typeof VERIFICATION_STATUSES)[number] })} className="lt-input mt-1 w-full text-sm">{VERIFICATION_STATUSES.map((status) => <option key={status}>{status}</option>)}</select></label><label className="text-xs text-[var(--text-muted)]"><span>Verification method</span><select required value={form.verification_method} onChange={(event) => setForm({ ...form, verification_method: event.target.value })} className="lt-input mt-1 w-full text-sm"><option value="">Select method</option>{verificationMethods.map((method) => <option key={method}>{method}</option>)}</select></label><Field label="Expiry date (optional)" value={form.expires_at} type="datetime-local" onChange={(value) => setForm({ ...form, expires_at: value })} /></div><div className="rounded border border-[var(--border)] bg-[var(--surface-muted)] p-3 text-sm"><p className="font-semibold">Evidence used: {activeEvidence.length}</p>{activeEvidence.length === 0 ? <p className="mt-1 text-amber-800">Add active evidence before verifying this claim.</p> : <ul className="mt-2 list-disc pl-5">{activeEvidence.map((link) => <li key={link.evidence_id}>{link.evidence.title} ({link.evidence.evidence_type})</li>)}</ul>}</div><label className="block text-xs text-[var(--text-muted)]"><span>Verification notes or reason</span><textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} maxLength={10000} className="lt-input mt-1 min-h-20 w-full text-sm" /></label><label className="flex items-start gap-2 text-sm"><input type="checkbox" checked={form.confirm} onChange={(event) => setForm({ ...form, confirm: event.target.checked })} className="mt-1" />I reviewed the evidence and confirm this historical verification result.</label><div className="flex gap-2"><button type="submit" disabled={working || !form.verification_method || !form.confirm} className="lt-btn lt-btn-primary text-sm">{working ? "Submitting..." : "Submit Verification"}</button><button type="button" onClick={onCancel} className="lt-btn lt-btn-secondary text-sm">Cancel</button></div></form>; }

function History({ title, empty, children }: { title: string; empty: string; children: React.ReactNode }) { const hasChildren = Array.isArray(children) ? children.length > 0 : Boolean(children); return <section className="lt-card p-5"><h3 className="font-semibold">{title}</h3>{hasChildren ? <div className="mt-2">{children}</div> : <p className="mt-3 text-sm text-[var(--text-muted)]">{empty}</p>}</section>; }
