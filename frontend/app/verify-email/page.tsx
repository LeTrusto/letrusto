"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import BrandMark from "@/components/layout/BrandMark";
import { confirmEmailVerification } from "@/services/auth.service";

export default function VerifyEmailPage() {
  const token = useSearchParams().get("token") ?? "";
  const [message, setMessage] = useState("");
  const [error, setError] = useState(token ? "" : "This verification link is invalid or expired.");

  useEffect(() => {
    if (!token) return;
    void confirmEmailVerification(token)
      .then((result) => setMessage(result.message))
      .catch((err) => setError(err instanceof Error ? err.message : "This verification link is invalid or expired."));
  }, [token]);

  return <main className="flex flex-1 items-center justify-center bg-[var(--background)] px-4 py-12"><section className="w-full max-w-[460px] rounded-[var(--radius-xl)] border border-[var(--border)] bg-[var(--surface)] p-6 text-center shadow-[0_8px_28px_rgba(107,33,168,0.08)] sm:p-9"><BrandMark /><h1 className="mt-7 text-3xl font-black text-[var(--text-primary)]">Verify your email</h1>{message && <p className="mt-5 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">{message}</p>}{error && <p role="alert" className="mt-5 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}<Link href="/login" className="lt-btn lt-btn-primary mt-6 inline-flex">Back to sign in</Link></section></main>;
}
