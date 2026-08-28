"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";

import BrandMark from "@/components/layout/BrandMark";
import { confirmPasswordReset } from "@/services/auth.service";

export default function ResetPasswordPage() {
  const token = useSearchParams().get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    if (password.length < 8) return setError("Password must be at least 8 characters");
    if (password !== confirm) return setError("Passwords do not match");
    setLoading(true);
    try {
      const result = await confirmPasswordReset(token, password);
      setMessage(result.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "This reset link is invalid or expired.");
    } finally {
      setLoading(false);
    }
  }

  return <main className="flex flex-1 items-center justify-center bg-[var(--background)] px-4 py-12 sm:py-16"><section className="w-full max-w-[460px] rounded-[var(--radius-xl)] border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_8px_28px_rgba(107,33,168,0.08)] sm:p-9"><div className="mb-8 flex flex-col items-center text-center"><BrandMark /><h1 className="mt-7 text-3xl font-black text-[var(--text-primary)]">Set a new password</h1><p className="mt-2 text-[var(--text-secondary)]">Choose a new password for your LeTrusto account.</p></div>{message ? <div className="space-y-5 text-center"><p className="rounded-lg border border-pink-200 bg-pink-50 px-4 py-3 text-sm text-[var(--text-primary)]">{message}</p><Link href="/login" className="lt-btn lt-btn-primary h-[52px] w-full rounded-lg">Back to sign in</Link></div> : <form onSubmit={(event) => { void handleSubmit(event); }} className="space-y-5">{error && <p role="alert" className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}<div><label htmlFor="new-password" className="mb-2 block text-sm font-semibold text-[var(--text-primary)]">New password</label><input id="new-password" type="password" required minLength={8} maxLength={64} value={password} onChange={(event) => setPassword(event.target.value)} className="lt-input h-[52px]" /></div><div><label htmlFor="confirm-password" className="mb-2 block text-sm font-semibold text-[var(--text-primary)]">Confirm password</label><input id="confirm-password" type="password" required minLength={8} maxLength={64} value={confirm} onChange={(event) => setConfirm(event.target.value)} className="lt-input h-[52px]" /></div><button type="submit" disabled={loading || !token} className="lt-btn lt-btn-primary h-[52px] w-full rounded-lg">{loading ? "Resetting..." : "Reset password"}</button></form>}</section></main>;
}