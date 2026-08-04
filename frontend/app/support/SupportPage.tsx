"use client";

import { ChevronDown, ChevronUp, Loader2, MessageCircle, Send } from "lucide-react";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { buildApiUrl, IS_API_CONFIGURED } from "@/services/api";

type FaqItem = { question: string; answer: string; category: string };
type ToastState = { type: "success" | "error"; message: string } | null;

const CATEGORIES = [
  { value: "contact", label: "General Enquiry" },
  { value: "feedback", label: "Feedback" },
  { value: "report_wrong", label: "Report Wrong Information" },
  { value: "report_broken", label: "Report Broken Link" },
  { value: "other", label: "Other" },
] as const;

function FaqAccordion({ items }: { items: FaqItem[] }) {
  const [openIdx, setOpenIdx] = useState<number | null>(null);
  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={i} className="rounded-2xl border border-gray-100 bg-white shadow-sm">
          <button
            onClick={() => setOpenIdx(openIdx === i ? null : i)}
            className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left text-sm font-semibold text-slate-800 hover:text-purple-700"
          >
            {item.question}
            {openIdx === i ? (
              <ChevronUp className="h-4 w-4 shrink-0 text-purple-500" />
            ) : (
              <ChevronDown className="h-4 w-4 shrink-0 text-gray-400" />
            )}
          </button>
          {openIdx === i && (
            <div className="border-t border-gray-100 px-5 py-4 text-sm text-gray-600">
              {item.answer}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default function SupportPage() {
  const searchParams = useSearchParams();
  const initialTab: "faq" | "contact" = searchParams.get("tab") === "contact" ? "contact" : "faq";
  const initialCategoryParam = searchParams.get("category");
  const initialCategory = CATEGORIES.some((item) => item.value === initialCategoryParam)
    ? initialCategoryParam
    : "contact";
  const [faq, setFaq] = useState<FaqItem[]>([]);
  const [form, setForm] = useState({ email: "", category: initialCategory, subject: "", body: "" });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [activeTab, setActiveTab] = useState<"faq" | "contact">(initialTab);
  const [toast, setToast] = useState<ToastState>(null);

  function dismissToastAfterDelay() {
    window.setTimeout(() => {
      setToast(null);
    }, 3500);
  }

  async function parseErrorMessage(res: Response) {
    const contentType = res.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      const payload = (await res.json().catch(() => ({}))) as { detail?: string; message?: string };
      return payload.detail ?? payload.message ?? `Ticket submission failed (${res.status}).`;
    }

    const text = (await res.text().catch(() => "")).trim();
    return text || `Ticket submission failed (${res.status}).`;
  }

  useEffect(() => {
    if (!IS_API_CONFIGURED) return;
    fetch(buildApiUrl("/support/faq"))
      .then((r) => r.json() as Promise<{ items: FaqItem[] }>)
      .then((d) => setFaq(d.items))
      .catch((err) => {
        console.error("[Support] FAQ load failed", err);
      });
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitError("");
    setToast(null);
    setSubmitting(true);
    try {
      const res = await fetch(buildApiUrl("/support/tickets"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        throw new Error(await parseErrorMessage(res));
      }

      const payload = (await res.json().catch(() => ({}))) as { message?: string };
      setSubmitted(true);
      setToast({
        type: "success",
        message: payload.message ?? "Ticket submitted successfully. Our team will contact you shortly.",
      });
      dismissToastAfterDelay();
    } catch (err) {
      const message =
        err instanceof TypeError
          ? "Unable to reach support service right now. Please check your connection and try again."
          : err instanceof Error
            ? err.message
            : "Unable to submit your support ticket right now. Please try again.";
      setSubmitError(message);
      setToast({ type: "error", message });
      dismissToastAfterDelay();
      console.error("[Support] Ticket submission failed", err);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-4xl px-5 py-10 sm:px-6">
      {toast && (
        <div
          className={`mb-4 rounded-xl border px-4 py-3 text-sm font-medium ${
            toast.type === "success"
              ? "border-green-200 bg-green-50 text-green-700"
              : "border-red-200 bg-red-50 text-red-700"
          }`}
          role="status"
          aria-live="polite"
        >
          {toast.message}
        </div>
      )}

      <div className="mb-8">
        <h1 className="text-3xl font-black text-slate-900">Support Centre</h1>
        <p className="mt-2 text-gray-500">Find answers or get in touch with our team</p>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-2 rounded-2xl bg-gray-100 p-1.5">
        {[
          { key: "faq", label: "FAQ" },
          { key: "contact", label: "Contact & Report" },
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key as "faq" | "contact")}
            className={`flex-1 rounded-xl py-2.5 text-sm font-bold transition ${
              activeTab === key
                ? "bg-white text-purple-700 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {activeTab === "faq" && (
        <div>
          {faq.length > 0 ? (
            <FaqAccordion items={faq} />
          ) : (
            <div className="rounded-2xl border border-gray-100 bg-white p-8 text-center text-gray-400">
              <MessageCircle className="mx-auto mb-3 h-10 w-10 opacity-30" />
              {IS_API_CONFIGURED
                ? "Loading FAQ…"
                : "FAQ available when backend is connected."}
            </div>
          )}
        </div>
      )}

      {activeTab === "contact" && (
        <div className="rounded-3xl border border-gray-100 bg-white p-8 shadow-sm">
          {submitted ? (
            <div className="py-10 text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                <Send className="h-7 w-7 text-green-600" />
              </div>
              <h2 className="mb-2 text-xl font-bold text-slate-900">Ticket Submitted!</h2>
              <p className="text-gray-500">
                We&apos;ll get back to you at <strong>{form.email}</strong> within 24–48 hours.
              </p>
              <button
                onClick={() => { setSubmitted(false); setForm({ email: "", category: "contact", subject: "", body: "" }); }}
                className="mt-6 text-sm font-semibold text-purple-700 hover:underline"
              >
                Submit another ticket
              </button>
            </div>
          ) : (
            <>
              <h2 className="mb-6 text-xl font-bold text-slate-900">Submit a Support Ticket</h2>
              {submitError && (
                <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {submitError}
                </div>
              )}
              <form onSubmit={(e) => { void handleSubmit(e); }} className="space-y-5">
                <div>
                  <label className="mb-1.5 block text-sm font-semibold text-gray-700">Email</label>
                  <input
                    type="email"
                    required
                    value={form.email}
                    onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                    className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-100"
                    placeholder="hello@letrusto.com"
                  />
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-semibold text-gray-700">Category</label>
                  <select
                    value={form.category}
                    onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                    className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-100"
                  >
                    {CATEGORIES.map((c) => (
                      <option key={c.value} value={c.value}>{c.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-semibold text-gray-700">Subject</label>
                  <input
                    type="text"
                    required
                    minLength={5}
                    value={form.subject}
                    onChange={(e) => setForm((f) => ({ ...f, subject: e.target.value }))}
                    className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-100"
                    placeholder="Brief description of your issue"
                  />
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-semibold text-gray-700">Message</label>
                  <textarea
                    required
                    minLength={10}
                    rows={5}
                    value={form.body}
                    onChange={(e) => setForm((f) => ({ ...f, body: e.target.value }))}
                    className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-100"
                    placeholder="Please describe your issue in detail…"
                  />
                </div>
                <button
                  type="submit"
                  disabled={submitting || !IS_API_CONFIGURED}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 py-3.5 text-sm font-bold text-white transition hover:scale-[1.02] disabled:opacity-60"
                >
                  {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  {submitting ? "Submitting…" : "Send Ticket"}
                </button>
                {!IS_API_CONFIGURED && (
                  <p className="text-center text-xs text-gray-400">Backend required to submit tickets</p>
                )}
              </form>
            </>
          )}
        </div>
      )}
    </main>
  );
}
