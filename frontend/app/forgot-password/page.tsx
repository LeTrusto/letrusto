"use client";

import Link from "next/link";
import { useState } from "react";

import BrandMark from "@/components/layout/BrandMark";
import { requestPasswordReset } from "@/services/auth.service";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await requestPasswordReset(email);
      setSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return <main className="flex flex-1 items-center justify-center bg-[var(--background)] px-4 py-12 sm:py-16"><section className="w-full max-w-[460px] rounded-[var(--radius-xl)] border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_8px_28px_rgba(107,33,168,0.08)] sm:p-9"><div className="mb-8 flex flex-col items-center text-center"><BrandMark /><h1 className="mt-7 text-3xl font-black text-[var(--text-primary)]">Forgot your password?</h1><p className="mt-2 text-[var(--text-secondary)]">Enter the email address associated with your account and we&apos;ll send you a reset link.</p></div>{sent ? <div className="space-y-5 text-center"><p className="rounded-lg border border-pink-200 bg-pink-50 px-4 py-3 text-sm text-[var(--text-primary)]">If an account exists for that email, a reset link has been sent.</p><Link href="/login" className="lt-btn lt-btn-primary h-[52px] w-full rounded-lg">Back to sign in</Link></div> : <form onSubmit={(event) => { void handleSubmit(event); }} className="space-y-5">{error && <p role="alert" className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}<div><label htmlFor="reset-email" className="mb-2 block text-sm font-semibold text-[var(--text-primary)]">Email address</label><input id="reset-email" type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Enter your email" className="lt-input h-[52px]" /></div><button type="submit" disabled={loading} className="lt-btn lt-btn-primary h-[52px] w-full rounded-lg">{loading ? "Sending..." : "Send reset link"}</button><Link href="/login" className="block text-center text-sm font-bold text-[var(--lt-primary)] hover:text-[var(--lt-accent-dark)]">Back to sign in</Link></form>}</section></main>;
}