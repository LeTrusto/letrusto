"use client";

import { Eye, EyeOff, Loader2, LogIn } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";

import BrandMark from "@/components/layout/BrandMark";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/dashboard";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (isAuthenticated) return null;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login({ email, password }, redirectTo);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Incorrect email or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-1 items-center justify-center bg-[var(--background)] px-4 py-12 sm:py-16">
      <section className="w-full max-w-[460px] rounded-[var(--radius-xl)] border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_8px_28px_rgba(107,33,168,0.08)] sm:p-9">
        <div className="mb-8 flex flex-col items-center text-center">
          <BrandMark />
          <h1 className="mt-7 text-3xl font-black text-[var(--text-primary)]">Welcome back</h1>
          <p className="mt-2 text-[var(--text-secondary)]">Sign in to your LeTrusto account</p>
        </div>

        {error && <p role="alert" className="mb-5 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}

        <form onSubmit={(event) => { void handleSubmit(event); }} className="space-y-5">
          <div>
            <label htmlFor="login-email" className="mb-2 block text-sm font-semibold text-[var(--text-primary)]">Email address</label>
            <input id="login-email" type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Enter your email" className="lt-input h-[52px]" />
          </div>
          <div>
            <div className="mb-2 flex items-center justify-between gap-3">
              <label htmlFor="login-password" className="block text-sm font-semibold text-[var(--text-primary)]">Password</label>
              <Link href="/forgot-password" className="text-sm font-semibold text-[var(--lt-accent-dark)] hover:text-[var(--lt-primary)]">Forgot password?</Link>
            </div>
            <div className="relative">
              <input id="login-password" type={showPassword ? "text" : "password"} required autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" maxLength={64} className="lt-input h-[52px] pr-12" />
              <button type="button" onClick={() => setShowPassword((visible) => !visible)} className="absolute right-3 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full text-[var(--text-secondary)] hover:bg-[var(--surface-muted)] hover:text-[var(--lt-primary)]" aria-label={showPassword ? "Hide password" : "Show password"}>
                {showPassword ? <EyeOff size={21} /> : <Eye size={21} />}
              </button>
            </div>
          </div>
          <button type="submit" disabled={loading} className="lt-btn lt-btn-primary flex h-[52px] w-full rounded-lg text-base">
            {loading ? <Loader2 size={20} className="animate-spin" /> : <LogIn size={20} />}
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="mt-7 text-center text-sm text-[var(--text-secondary)]">Don&apos;t have an account? <Link href="/register" className="font-bold text-[var(--lt-primary)] hover:text-[var(--lt-accent-dark)]">Create account</Link></p>
      </section>
    </main>
  );
}
