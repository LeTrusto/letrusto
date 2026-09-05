"use client";

import { Eye, EyeOff, Loader2, LogIn } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import BrandMark from "@/components/layout/BrandMark";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/dashboard";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [redirectTimedOut, setRedirectTimedOut] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;
    const timer = window.setTimeout(() => setRedirectTimedOut(true), 2000);
    router.replace(redirectTo);
    return () => window.clearTimeout(timer);
  }, [isAuthenticated, redirectTo, router]);

  if (isLoading) return <AuthLoading />;
  if (isAuthenticated) return <AuthRedirectFallback timedOut={redirectTimedOut} onSignOut={() => void logout()} />;

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
    <main className="relative flex flex-1 items-center justify-center overflow-hidden bg-slate-950 px-4 py-12 sm:py-16"><div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(37,99,235,0.28),transparent_30%),radial-gradient(circle_at_85%_80%,rgba(20,184,166,0.18),transparent_28%)]" />
      <section className="relative w-full max-w-[460px] rounded-[1.5rem] border border-white/20 bg-[var(--surface)] p-6 shadow-2xl sm:p-9">
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

function AuthLoading({ message = "Loading..." }: { message?: string }) {
  return <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-sm text-slate-300">{message}</main>;
}

function AuthRedirectFallback({ timedOut, onSignOut }: { timedOut: boolean; onSignOut: () => void }) {
  return <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-center text-slate-300"><div><p>{timedOut ? "Redirect is taking longer than expected." : "You are already signed in. Redirecting..."}</p>{timedOut && <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:justify-center"><Link href="/dashboard" className="rounded-lg bg-[#2563eb] px-4 py-2.5 text-sm font-bold text-white">Click here to go to Dashboard</Link><button type="button" onClick={onSignOut} className="rounded-lg border border-slate-700 px-4 py-2.5 text-sm font-bold text-slate-300 hover:border-slate-500 hover:text-white">Sign Out &amp; Switch Account</button></div>}</div></main>;
}
