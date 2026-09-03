"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { LogOut, Package, UserRound } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { getAccount, updateAccountProfile } from "@/services/account.service";
import type { CustomerAccount } from "@/types/account";
import DigitalPurchases from "@/components/account/DigitalPurchases";

export default function AccountPage() {
  const { accessToken, isLoading, isAuthenticated, logout } = useAuth();
  const [account, setAccount] = useState<CustomerAccount | null>(null);
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!accessToken) return;
    void getAccount(accessToken)
      .then((data) => {
        setAccount(data);
        setName(data.full_name);
      })
      .catch(() => setError("Unable to load your account."));
  }, [accessToken]);

  async function saveProfile(event: React.FormEvent) {
    event.preventDefault();
    if (!accessToken || !name.trim()) return;
    setMessage("");
    setError("");
    try {
      const updated = await updateAccountProfile(accessToken, { full_name: name.trim() });
      setAccount(updated);
      setMessage("Profile updated.");
    } catch {
      setError("Unable to update your profile.");
    }
  }

  if (isLoading) return <main className="mx-auto max-w-3xl px-4 py-16 text-center">Loading account...</main>;
  if (!isAuthenticated) {
    return <main className="mx-auto max-w-3xl px-4 py-16 text-center"><UserRound className="mx-auto text-[var(--text-muted)]" /><h1 className="lt-heading-2 mt-4">Sign in to your account</h1><Link href="/login?redirect=/account" className="lt-btn lt-btn-primary mt-6 inline-flex">Sign In</Link></main>;
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-10 md:px-6 md:py-16">
      <div className="rounded-2xl bg-[#26113c] p-6 text-white shadow-xl sm:p-8"><div className="flex items-start justify-between gap-4">
        <div><p className="lt-label">Customer account</p><h1 className="lt-heading-1 mt-2">{account?.full_name || "Your account"}</h1><p className="mt-2 text-sm text-[var(--text-secondary)]">{account?.email}</p></div>
        <button onClick={() => void logout("/")} className="lt-btn lt-btn-sm border border-white/20 text-white hover:bg-white/10"><LogOut size={15} /> Log out</button>
      </div></div>

      {error && <p role="alert" className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <Link href="/account/orders" className="lt-card lt-card-hover flex items-center gap-4"><Package className="text-[var(--lt-accent-dark)]" /><div><h2 className="font-bold">My orders</h2><p className="mt-1 text-sm text-[var(--text-secondary)]">View order history and tracking</p></div></Link>
        <div className="lt-card"><p className="lt-label">Member since</p><p className="mt-2 text-sm font-semibold">{account ? new Date(account.created_at).toLocaleDateString("en-IN") : "—"}</p><Link href="/digital-products" className="mt-4 inline-flex items-center text-sm font-bold text-[var(--lt-primary)]">Browse digital products</Link></div>
      </div>

      <DigitalPurchases />

      <form onSubmit={saveProfile} className="lt-card mt-8">
        <h2 className="text-lg font-bold">Profile</h2>
        <label htmlFor="account-name" className="lt-label mt-5 block">Name</label>
        <input id="account-name" value={name} onChange={(event) => setName(event.target.value)} className="lt-input mt-2" />
        <label className="lt-label mt-5 block">Email</label>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">{account?.email}</p>
        <p className="mt-5 text-xs text-[var(--text-muted)]">Phone and saved addresses are not available in the current account model.</p>
        <div className="mt-5 flex items-center gap-4"><button type="submit" className="lt-btn lt-btn-primary">Save profile</button>{message && <span className="text-sm text-[var(--lt-success)]">{message}</span>}</div>
      </form>
    </main>
  );
}
