"use client";

import { Eye, EyeOff, Loader2, UserPlus } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import BrandMark from "@/components/layout/BrandMark";
import { useAuth } from "@/hooks/useAuth";

export default function RegisterPage() {
  const { register, isAuthenticated } = useAuth();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (isAuthenticated) return null;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    if (form.password.length < 8) return setError("Password must be at least 8 characters");
    if (form.password !== form.confirm) return setError("Passwords do not match");
    setLoading(true);
    try {
      await register({ email: form.email, password: form.password, full_name: form.full_name });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-1 items-center justify-center bg-[var(--background)] px-4 py-12 sm:py-16">
      <section className="w-full max-w-[460px] rounded-[var(--radius-xl)] border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_8px_28px_rgba(107,33,168,0.08)] sm:p-9">
        <div className="mb-8 flex flex-col items-center text-center">
          <BrandMark />
          <h1 className="mt-7 text-3xl font-black text-[var(--text-primary)]">Create your LeTrusto account</h1>
          <p className="mt-2 text-[var(--text-secondary)]">Join us for fresh designs, printed on demand.</p>
        </div>
        {error && <p role="alert" className="mb-5 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}
        <form onSubmit={(event) => { void handleSubmit(event); }} className="space-y-4">
          <div><label htmlFor="register-name" className="mb-2 block text-sm font-semibold text-[var(--text-primary)]">Full name</label><input id="register-name" type="text" required autoComplete="name" value={form.full_name} onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))} placeholder="Your full name" className="lt-input h-[52px]" /></div>
          <div><label htmlFor="register-email" className="mb-2 block text-sm font-semibold text-[var(--text-primary)]">Email address</label><input id="register-email" type="email" required autoComplete="email" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} placeholder="Enter your email" className="lt-input h-[52px]" /></div>
          <PasswordField id="register-password" label="Password" value={form.password} visible={showPassword} onChange={(value) => setForm((current) => ({ ...current, password: value }))} onToggle={() => setShowPassword((visible) => !visible)} autoComplete="new-password" placeholder="At least 8 characters" />
          <PasswordField id="register-confirm" label="Confirm password" value={form.confirm} visible={showConfirm} onChange={(value) => setForm((current) => ({ ...current, confirm: value }))} onToggle={() => setShowConfirm((visible) => !visible)} autoComplete="new-password" placeholder="Repeat your password" />
          <button type="submit" disabled={loading} className="lt-btn lt-btn-primary mt-2 flex h-[52px] w-full rounded-lg text-base">{loading ? <Loader2 size={20} className="animate-spin" /> : <UserPlus size={20} />}{loading ? "Creating account..." : "Create account"}</button>
        </form>
        <p className="mt-7 text-center text-sm text-[var(--text-secondary)]">Already have an account? <Link href="/login" className="font-bold text-[var(--lt-primary)] hover:text-[var(--lt-accent-dark)]">Sign in</Link></p>
      </section>
    </main>
  );
}

function PasswordField({ id, label, value, visible, onChange, onToggle, autoComplete, placeholder }: { id: string; label: string; value: string; visible: boolean; onChange: (value: string) => void; onToggle: () => void; autoComplete: string; placeholder: string }) {
  return <div><label htmlFor={id} className="mb-2 block text-sm font-semibold text-[var(--text-primary)]">{label}</label><div className="relative"><input id={id} type={visible ? "text" : "password"} required autoComplete={autoComplete} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} minLength={8} maxLength={64} className="lt-input h-[52px] pr-12" /><button type="button" onClick={onToggle} className="absolute right-3 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full text-[var(--text-secondary)] hover:bg-[var(--surface-muted)] hover:text-[var(--lt-primary)]" aria-label={visible ? `Hide ${label.toLowerCase()}` : `Show ${label.toLowerCase()}`}>{visible ? <EyeOff size={21} /> : <Eye size={21} />}</button></div></div>;
}
