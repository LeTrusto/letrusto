"use client";

import { Bell, CheckCheck, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { listNotifications, markAllNotificationsRead, markNotificationRead, type NotificationItem } from "@/services/notification.service";

type NotificationCenterProps = { admin?: boolean };

export function notificationTarget(notification: NotificationItem, admin: boolean): string | null {
  if (!notification.related_entity_id) return null;
  if (notification.related_entity_type === "PROPERTY") return admin ? `/admin/properties/${notification.related_entity_id}` : `/seller/properties/${notification.related_entity_id}`;
  if (notification.related_entity_type === "ENQUIRY") return admin ? "/admin/enquiries" : `/seller/leads/${notification.related_entity_id}`;
  return null;
}

function relativeTime(value: string): string {
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 1000));
  if (seconds < 60) return "Just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export default function NotificationCenter({ admin = false }: NotificationCenterProps) {
  const { accessToken } = useAuth();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true); setError(false);
    try { const result = await listNotifications(accessToken); setItems(result.notifications); setUnreadCount(result.unread_count); } catch { setError(true); } finally { setLoading(false); }
  }, [accessToken]);

  useEffect(() => { if (open) void Promise.resolve().then(() => load()); }, [open, load]);

  async function openNotification(notification: NotificationItem) {
    if (!accessToken) return;
    if (!notification.is_read) { await markNotificationRead(accessToken, notification.id); setItems((current) => current.map((item) => item.id === notification.id ? { ...item, is_read: true } : item)); setUnreadCount((count) => Math.max(0, count - 1)); }
    const target = notificationTarget(notification, admin);
    if (target) { setOpen(false); router.push(target); }
  }

  async function markAllRead() {
    if (!accessToken || unreadCount === 0) return;
    await markAllNotificationsRead(accessToken);
    setItems((current) => current.map((item) => ({ ...item, is_read: true })));
    setUnreadCount(0);
  }

  return <div className="notification-center"><button type="button" className="notification-trigger" aria-label="Notifications" aria-expanded={open} onClick={() => setOpen((value) => !value)}><Bell size={17} />{unreadCount > 0 && <span className="notification-count">{unreadCount > 99 ? "99+" : unreadCount}</span>}</button>{open && <section className="notification-panel" aria-label="Notifications"><div className="notification-panel-heading"><div><p className="notification-kicker">Updates</p><h2>Notifications</h2></div><button type="button" className="notification-mark-all" onClick={() => void markAllRead()} disabled={unreadCount === 0}><CheckCheck size={15} /> Mark all read</button></div>{loading ? <p className="notification-state">Loading notifications...</p> : error ? <div className="notification-state"><p>Notifications couldn&apos;t be loaded.</p><button type="button" onClick={() => void load()}><RefreshCw size={14} /> Try again</button></div> : items.length === 0 ? <p className="notification-state">You&apos;re all caught up.</p> : <div className="notification-list">{items.map((notification) => <button type="button" className={`notification-item ${notification.is_read ? "read" : "unread"}`} key={notification.id} onClick={() => void openNotification(notification)}><span className="notification-item-dot" /><span className="notification-item-copy"><strong>{notification.title}</strong><span>{notification.body}</span><time dateTime={notification.created_at}>{relativeTime(notification.created_at)}</time></span></button>)}</div>}</section>}</div>;
}