import { authenticatedApiRequest } from "@/services/api";

export type NotificationItem = {
  id: number;
  type: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
  related_entity_type: string | null;
  related_entity_id: string | null;
};

export type NotificationList = { notifications: NotificationItem[]; unread_count: number };

export function listNotifications(token: string) { return authenticatedApiRequest<NotificationList>(token, "/notifications?limit=20"); }
export function markNotificationRead(token: string, id: number) { return authenticatedApiRequest<void>(token, `/notifications/${id}/read`, { method: "PATCH" }); }
export function markAllNotificationsRead(token: string) { return authenticatedApiRequest<void>(token, "/notifications/read-all", { method: "POST" }); }