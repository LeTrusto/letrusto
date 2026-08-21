"use client";

import { Eye, EyeOff, Loader2, LogIn, Smartphone } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { requestOtp } from "@/services/auth.service";

export default function LoginPage() {
  const { login, loginWithOtp, isAuthenticated } = useAuth();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/dashboard";
  const [mode, setMode] = useState<"mobile" | "email">(() => searchParams.get("method") === "email" ? "email" : "mobile");
  const [form, setForm] = useState({ email: "", password: "" });
  const [mobile, setMobile] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (isAuthenticated) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "mobile") {
        await loginWithOtp({ mobile_number: mobile, otp });
        window.location.assign(redirectTo);
      } else {
        await login({ email: form.email, password: form.password }, redirectTo);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleRequestOtp() {
    setError("");
    setLoading(true);
    try {
      await requestOtp({ mobile_number: mobile });
      setOtpSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to send OTP");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-1 items-center justify-center bg-gradient-to-br from-purple-50 via-pink-50 to-white px-4 py-16">
      <div className="w-full max-w-md">
        <div className="rounded-3xl border border-white/80 bg-white/90 p-8 shadow-2xl backdrop-blur-xl">
          <div className="mb-8 text-center">
            <Image src="/LeTrusto%20Brand%20Logo.png" alt="LeTrusto - Discover. Choose. Trust." width={1774} height={887} priority unoptimized className="mx-auto h-auto w-48" />
            <h1 className="mt-5 text-3xl font-black text-slate-900">Welcome back</h1>
            <p className="mt-2 text-gray-500">Login / Sign up</p>
          </div>
          <div className="mb-6 grid grid-cols-2 rounded-xl bg-gray-100 p-1">
            <button type="button" onClick={() => { setMode("mobile"); setError(""); }} className={`rounded-lg px-3 py-2 text-sm font-semibold ${mode === "mobile" ? "bg-white text-purple-700 shadow-sm" : "text-gray-500"}`}>Login with Mobile</button>
            <button type="button" onClick={() => { setMode("email"); setError(""); }} className={`rounded-lg px-3 py-2 text-sm font-semibold ${mode === "email" ? "bg-white text-purple-700 shadow-sm" : "text-gray-500"}`}>Login with Email</button>
          </div>
          {error && <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
          {mode === "mobile" ? (
            <form onSubmit={(e) => { void handleSubmit(e); }} className="space-y-5">
              <div><label className="mb-1.5 block text-sm font-semibold text-gray-700">Mobile number</label><input type="tel" required autoComplete="tel" value={mobile} onChange={(e) => setMobile(e.target.value)} className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none transition focus:border-purple-400 focus:bg-white focus:ring-2 focus:ring-purple-100" placeholder="+91 98765 43210" /></div>
              {otpSent && <div><label className="mb-1.5 block text-sm font-semibold text-gray-700">OTP</label><input type="text" required inputMode="numeric" autoComplete="one-time-code" value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))} className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm tracking-[0.35em] outline-none transition focus:border-purple-400 focus:bg-white focus:ring-2 focus:ring-purple-100" placeholder="000000" /></div>}
              {!otpSent ? <button type="button" disabled={loading} onClick={() => { void handleRequestOtp(); }} className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 py-3.5 text-sm font-bold text-white transition hover:scale-[1.02] disabled:opacity-60">{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Smartphone className="h-4 w-4" />}Send OTP</button> : <button type="submit" disabled={loading || otp.length !== 6} className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 py-3.5 text-sm font-bold text-white transition hover:scale-[1.02] disabled:opacity-60">{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <LogIn className="h-4 w-4" />}Verify OTP</button>}
            </form>
          ) : (
            <form onSubmit={(e) => { void handleSubmit(e); }} className="space-y-5">
              <div><label className="mb-1.5 block text-sm font-semibold text-gray-700">Email address</label><input type="email" required autoComplete="email" value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none transition focus:border-purple-400 focus:bg-white focus:ring-2 focus:ring-purple-100" placeholder="hello@letrusto.com" /></div>
              <div><label className="mb-1.5 block text-sm font-semibold text-gray-700">Password</label><div className="relative"><input type={showPwd ? "text" : "password"} required autoComplete="current-password" value={form.password} onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))} className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 pr-12 text-sm outline-none transition focus:border-purple-400 focus:bg-white focus:ring-2 focus:ring-purple-100" placeholder="••••••••" maxLength={64} /><button type="button" onClick={() => setShowPwd((s) => !s)} className="absolute right-4 top-3.5 text-gray-400 hover:text-gray-600" aria-label={showPwd ? "Hide password" : "Show password"}>{showPwd ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</button></div></div>
              <button type="submit" disabled={loading} className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 py-3.5 text-sm font-bold text-white transition hover:scale-[1.02] disabled:opacity-60">{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <LogIn className="h-4 w-4" />}{loading ? "Signing in…" : "Sign In"}</button>
            </form>
          )}
          <p className="mt-6 text-center text-sm text-gray-500">Don&apos;t have an account? <Link href="/register" className="font-semibold text-purple-700 hover:underline">Create one free</Link></p>
        </div>
      </div>
    </main>
  );
}
