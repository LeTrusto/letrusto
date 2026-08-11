"use client";

import { Bell, GitCompare, Heart, Loader2, LogIn, Scale, Sparkles, TrendingDown, User } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { API_BASE_URL } from "@/services/api";

type DashboardData = {
  user: { id: string; email: string; full_name: string; role: string; created_at: string };
  favorites_count: number;
  saved_comparisons: Array<{ id: number; product_ids: string[]; label: string; created_at: string }>;
  price_alerts: Array<{
    id: number;
    product_id: string;
    product_name: string;
    current_price: number;
    target_price: number | null;
    is_active: boolean;
    created_at: string;
  }>;
  unread_notifications: number;
  recent_conversations_count: number;
};

export default function DashboardPage() {
  const { user, accessToken, isLoading, isAuthenticated } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [fetchError, setFetchError] = useState("");

  useEffect(() => {
    if (!accessToken) return;
    fetch(`${API_BASE_URL}/api/v1/users/dashboard`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error("Failed to load dashboard");
        return r.json() as Promise<DashboardData>;
      })
      .then(setData)
      .catch((e: unknown) => {
        setFetchError(e instanceof Error ? e.message : "Failed to load dashboard");
      });
  }, [accessToken]);

  if (isLoading) {
    return (
      <main className="flex flex-1 items-center justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
      </main>
    );
  }

  if (!isAuthenticated) {
    return (
      <main className="flex flex-1 flex-col items-center justify-center gap-6 py-24 text-center">
        <LogIn className="h-12 w-12 text-purple-300" />
        <h1 className="text-2xl font-bold text-slate-900">Sign in to view your dashboard</h1>
        <Link
          href="/login"
          className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 text-sm font-bold text-white"
        >
          Sign In
        </Link>
      </main>
    );
  }

  const displayUser = data?.user ?? user;

  return (
    <main className="mx-auto max-w-7xl px-5 py-10 sm:px-6">
      {/* Header */}
      <div className="mb-8 flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500">
          <User className="h-7 w-7 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-black text-slate-900">
            Hello, {displayUser?.full_name || displayUser?.email} 👋
          </h1>
          <p className="text-sm text-gray-500">{displayUser?.email}</p>
        </div>
      </div>

      {fetchError && (
        <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          {fetchError} — showing cached profile only.
        </div>
      )}

      {/* Stats Grid */}
      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { icon: Heart, label: "Favourites", value: data?.favorites_count ?? 0, href: "/favorites", color: "text-pink-600" },
          { icon: Scale, label: "Saved Comparisons", value: data?.saved_comparisons.length ?? 0, href: "/compare", color: "text-purple-600" },
          { icon: TrendingDown, label: "Price Alerts", value: data?.price_alerts.length ?? 0, href: "#alerts", color: "text-green-600" },
          { icon: Bell, label: "Notifications", value: data?.unread_notifications ?? 0, href: "/notifications", color: "text-orange-600" },
        ].map(({ icon: Icon, label, value, href, color }) => (
          <Link
            key={label}
            href={href}
            className="group rounded-2xl border border-gray-100 bg-white p-5 shadow-sm transition hover:shadow-md"
          >
            <Icon className={`mb-2 h-6 w-6 ${color}`} />
            <div className="text-2xl font-black text-slate-900">{value}</div>
            <div className="text-sm text-gray-500">{label}</div>
          </Link>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Saved Comparisons */}
        <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900">Saved Comparisons</h2>
            <Link href="/compare" className="text-sm font-semibold text-purple-700 hover:underline">
              View all
            </Link>
          </div>
          {data && data.saved_comparisons.length > 0 ? (
            <ul className="space-y-3">
              {data.saved_comparisons.slice(0, 5).map((c) => (
                <li key={c.id} className="rounded-xl bg-gray-50 px-4 py-3">
                  <div className="font-semibold text-sm text-slate-800">
                    {c.label || `Comparison ${c.id}`}
                  </div>
                  <div className="mt-0.5 text-xs text-gray-500">
                    {c.product_ids.length} products · {new Date(c.created_at).toLocaleDateString()}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="py-8 text-center text-sm text-gray-400">
              <GitCompare className="mx-auto mb-2 h-8 w-8 opacity-30" />
              No saved comparisons yet.{" "}
              <Link href="/compare" className="text-[var(--lt-purple)] hover:underline">
                Try comparing AI tools
              </Link>
            </div>
          )}
        </section>

        {/* Price Alerts */}
        <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm" id="alerts">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900">Price Alerts</h2>
          </div>
          {data && data.price_alerts.length > 0 ? (
            <ul className="space-y-3">
              {data.price_alerts.map((a) => (
                <li key={a.id} className="flex items-center justify-between rounded-xl bg-gray-50 px-4 py-3">
                  <div>
                    <div className="font-semibold text-sm text-slate-800 truncate max-w-[200px]">{a.product_name}</div>
                    <div className="text-xs text-gray-500">
                      Current: ₹{a.current_price.toLocaleString()}
                      {a.target_price && ` · Target: ₹${a.target_price.toLocaleString()}`}
                    </div>
                  </div>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-bold ${a.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                    {a.is_active ? "Active" : "Triggered"}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="py-8 text-center text-sm text-gray-400">
              <TrendingDown className="mx-auto mb-2 h-8 w-8 opacity-30" />
              No price alerts set.
            </div>
          )}
        </section>

        {/* AI Conversations */}
        <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900">AI Conversations</h2>
            <Link href="/ai" className="text-sm font-semibold text-purple-700 hover:underline">
              Start new
            </Link>
          </div>
          <div className="py-6 text-center text-sm text-gray-400">
            <Sparkles className="mx-auto mb-2 h-8 w-8 opacity-30" />
            {data?.recent_conversations_count
              ? `${data.recent_conversations_count} conversation${data.recent_conversations_count > 1 ? "s" : ""} saved`
              : "No conversations yet."}
            <br />
            <Link href="/ai" className="mt-2 inline-block text-purple-600 hover:underline">
              Ask the AI assistant
            </Link>
          </div>
        </section>

        {/* Quick Links */}
        <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-bold text-slate-900">Quick Links</h2>
          <div className="grid grid-cols-2 gap-3">
            {[
              { href: "/favorites", label: "My Favourites", icon: Heart },
              { href: "/compare", label: "Compare Tools", icon: Scale },
              { href: "/ai", label: "AI Assistant", icon: Sparkles },
              { href: "/notifications", label: "Notifications", icon: Bell },
              { href: "/guides", label: "Buying Guides", icon: TrendingDown },
              { href: "/support", label: "Support", icon: User },
            ].map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className="flex items-center gap-2 rounded-xl border border-gray-100 bg-gray-50 px-3 py-2.5 text-sm font-semibold text-gray-700 transition hover:bg-purple-50 hover:text-purple-700"
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
