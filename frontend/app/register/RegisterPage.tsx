"use client";

import { Eye, EyeOff, Loader2, UserPlus } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import BrandMark from "@/components/layout/BrandMark";
import { useAuth } from "@/hooks/useAuth";
import { trackSafeEvent } from "@/lib/analytics";
import { recordMarketingEvent } from "@/services/marketing.service";

export default function RegisterPage() {
  const { register, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [redirectTimedOut, setRedirectTimedOut] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;
    const timer = window.setTimeout(() => setRedirectTimedOut(true), 2000);
    router.replace("/dashboard");
    return () => window.clearTimeout(timer);
  }, [isAuthenticated, router]);

  if (isLoading) return <AuthLoading />;
  if (isAuthenticated) return <AuthRedirectFallback timedOut={redirectTimedOut} onSignOut={() => void logout()} />;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    trackSafeEvent("signup_started", { source: "register_page" });
    if (form.password.length < 8) return setError("Password must be at least 8 characters");
    if (form.password !== form.confirm) return setError("Passwords do not match");
    setLoading(true);
    try {
      await register({ email: form.email, password: form.password, full_name: form.full_name });
      trackSafeEvent("account_created", { source: "register_page" });
      void recordMarketingEvent("account_created", { source: "register_page" }).catch(() => undefined);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative flex flex-1 items-center justify-center overflow-hidden bg-slate-950 px-4 py-12 sm:py-16"><div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(37,99,235,0.28),transparent_30%),radial-gradient(circle_at_85%_80%,rgba(20,184,166,0.18),transparent_28%)]" />
      <section className="relative w-full max-w-[460px] rounded-[1.5rem] border border-white/20 bg-[var(--surface)] p-6 shadow-2xl sm:p-9">
        <div className="mb-8 flex flex-col items-center text-center">
          <BrandMark />
          <h1 className="mt-7 text-3xl font-black text-[var(--text-primary)]">Create your LeTrusto account</h1>
          <p className="mt-2 text-[var(--text-secondary)]">Save your work and access your digital purchases.</p>
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

function AuthLoading({ message = "Loading..." }: { message?: string }) {
  return <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-sm text-slate-300">{message}</main>;
}

function AuthRedirectFallback({ timedOut, onSignOut }: { timedOut: boolean; onSignOut: () => void }) {
  return <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-center text-slate-300"><div><p>{timedOut ? "Redirect is taking longer than expected." : "You are already signed in. Redirecting..."}</p>{timedOut && <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:justify-center"><Link href="/dashboard" className="rounded-lg bg-[#2563eb] px-4 py-2.5 text-sm font-bold text-white">Click here to go to Dashboard</Link><button type="button" onClick={onSignOut} className="rounded-lg border border-slate-700 px-4 py-2.5 text-sm font-bold text-slate-300 hover:border-slate-500 hover:text-white">Sign Out &amp; Switch Account</button></div>}</div></main>;
}

function PasswordField({ id, label, value, visible, onChange, onToggle, autoComplete, placeholder }: { id: string; label: string; value: string; visible: boolean; onChange: (value: string) => void; onToggle: () => void; autoComplete: string; placeholder: string }) {
  return <div><label htmlFor={id} className="mb-2 block text-sm font-semibold text-[var(--text-primary)]">{label}</label><div className="relative"><input id={id} type={visible ? "text" : "password"} required autoComplete={autoComplete} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} minLength={8} maxLength={64} className="lt-input h-[52px] pr-12" /><button type="button" onClick={onToggle} className="absolute right-3 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full text-[var(--text-secondary)] hover:bg-[var(--surface-muted)] hover:text-[var(--lt-primary)]" aria-label={visible ? `Hide ${label.toLowerCase()}` : `Show ${label.toLowerCase()}`}>{visible ? <EyeOff size={21} /> : <Eye size={21} />}</button></div></div>;
}
