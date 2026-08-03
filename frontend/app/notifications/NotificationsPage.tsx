"use client";

import { Bell, CheckCheck, Loader2, LogIn } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { API_BASE_URL } from "@/services/api";

type NotificationItem = {
  id: number;
  type: string;
  title: string;
  body: string;
  product_id: string | null;
  is_read: boolean;
  created_at: string;
};

const TYPE_COLORS: Record<string, string> = {
  price_drop: "bg-green-100 text-green-700",
  new_product: "bg-blue-100 text-blue-700",
  deal: "bg-orange-100 text-orange-700",
  ai_recommendation: "bg-purple-100 text-purple-700",
  stock: "bg-red-100 text-red-700",
  wishlist: "bg-pink-100 text-pink-700",
};

export default function NotificationsPage() {
  const { accessToken, isLoading, isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unread, setUnread] = useState(0);
  const [fetchDone, setFetchDone] = useState(false);
  // Derived: loading if auth is loading, or user is authenticated but fetch not done yet
  const loading = isLoading || (!isLoading && isAuthenticated && !fetchDone);

  useEffect(() => {
    if (isLoading || !accessToken) return; // wait for auth to resolve
    fetch(`${API_BASE_URL}/api/v1/notifications`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then((r) => r.json() as Promise<{ notifications: NotificationItem[]; unread_count: number }>)
      .then((d) => { setNotifications(d.notifications); setUnread(d.unread_count); setFetchDone(true); })
      .catch(() => { setFetchDone(true); });
  }, [isLoading, accessToken]);

  async function markAllRead() {
    if (!accessToken) return;
    await fetch(`${API_BASE_URL}/api/v1/notifications/read-all`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    setNotifications((n) => n.map((x) => ({ ...x, is_read: true })));
    setUnread(0);
  }

  async function markOneRead(id: number) {
    if (!accessToken) return;
    await fetch(`${API_BASE_URL}/api/v1/notifications/${id}/read`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    setNotifications((n) => n.map((x) => x.id === id ? { ...x, is_read: true } : x));
    setUnread((u) => Math.max(0, u - 1));
  }

  if (isLoading || loading) {
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
        <h1 className="text-2xl font-bold text-slate-900">Sign in to view notifications</h1>
        <Link href="/login" className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 text-sm font-bold text-white">
          Sign In
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-5 py-10 sm:px-6">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bell className="h-6 w-6 text-purple-600" />
          <h1 className="text-2xl font-black text-slate-900">Notifications</h1>
          {unread > 0 && (
            <span className="rounded-full bg-pink-600 px-2.5 py-0.5 text-sm font-bold text-white">
              {unread}
            </span>
          )}
        </div>
        {unread > 0 && (
          <button
            onClick={() => { void markAllRead(); }}
            className="flex items-center gap-2 rounded-xl border border-purple-200 bg-white px-3 py-2 text-sm font-semibold text-purple-700 hover:bg-purple-50"
          >
            <CheckCheck className="h-4 w-4" />
            Mark all read
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="py-16 text-center text-gray-400">
          <Bell className="mx-auto mb-4 h-12 w-12 opacity-30" />
          <p className="text-lg">No notifications yet.</p>
        </div>
      ) : (
        <ul className="space-y-3">
          {notifications.map((n) => (
            <li
              key={n.id}
              onClick={() => { if (!n.is_read) void markOneRead(n.id); }}
              className={`cursor-pointer rounded-2xl border p-4 transition hover:shadow-md ${
                n.is_read ? "border-gray-100 bg-white" : "border-purple-100 bg-purple-50"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="mb-1 flex items-center gap-2">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-bold ${TYPE_COLORS[n.type] ?? "bg-gray-100 text-gray-600"}`}>
                      {n.type.replace(/_/g, " ")}
                    </span>
                    {!n.is_read && (
                      <span className="h-2 w-2 rounded-full bg-purple-500" />
                    )}
                  </div>
                  <div className="font-semibold text-sm text-slate-800">{n.title}</div>
                  <div className="mt-0.5 text-sm text-gray-500">{n.body}</div>
                </div>
                <time className="shrink-0 text-xs text-gray-400">
                  {new Date(n.created_at).toLocaleDateString()}
                </time>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
