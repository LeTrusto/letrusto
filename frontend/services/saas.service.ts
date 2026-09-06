import { authenticatedApiRequest } from "@/services/api";

export type Widget = {
  id: string;
  user_id: string;
  name: string;
  domain_name: string;
  theme_color: string;
  position: "bottom-left" | "bottom-right" | "top-left" | "top-right";
  display_delay: number;
  is_active: boolean;
  created_at: string;
};

export type WidgetDraft = Omit<Widget, "id" | "user_id" | "created_at">;

export type WidgetEvent = {
  id: string;
  widget_id: string;
  customer_name: string;
  customer_location: string | null;
  action_text: string | null;
  avatar_url: string | null;
  rating: number | null;
  review_text: string | null;
  is_approved: boolean;
  created_at: string;
};

export type EventDraft = {
  customer_name: string;
  customer_location?: string;
  action_text?: string;
  rating?: number;
  review_text?: string;
  is_approved: boolean;
};

export type SubscriptionCheckout = {
  subscription_id: string;
  plan_name: string;
  key_id: string;
  status: string;
};

export type Entitlement = {
  plan: "free" | "starter" | "pro";
  status: string;
  active: boolean;
  is_trial: boolean;
  trial_ends_at: string | null;
  max_widgets: number | null;
  monthly_view_limit: number | null;
  features: string[];
  subscription_id: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
};

export async function getWidgets(token: string) {
  return authenticatedApiRequest<Widget[]>(token, "/widgets");
}

export async function createWidget(token: string, draft: WidgetDraft) {
  return authenticatedApiRequest<Widget>(token, "/widgets", {
    method: "POST",
    body: JSON.stringify(draft),
  });
}

export async function updateWidget(token: string, id: string, draft: Partial<WidgetDraft>) {
  return authenticatedApiRequest<Widget>(token, `/widgets/${id}`, {
    method: "PUT",
    body: JSON.stringify(draft),
  });
}

export async function deactivateWidget(token: string, id: string) {
  return authenticatedApiRequest<Widget>(token, `/widgets/${id}`, { method: "DELETE" });
}

export async function getWidgetEvents(token: string, widgetId: string) {
  return authenticatedApiRequest<WidgetEvent[]>(token, `/widgets/${widgetId}/events`);
}

export async function createWidgetEvent(token: string, widgetId: string, draft: EventDraft) {
  return authenticatedApiRequest<WidgetEvent>(token, `/widgets/${widgetId}/events`, {
    method: "POST",
    body: JSON.stringify(draft),
  });
}

export async function hideWidgetEvent(token: string, eventId: string) {
  return authenticatedApiRequest<WidgetEvent>(token, `/events/${eventId}`, { method: "DELETE" });
}

export async function createSubscription(token: string, planName: "starter" | "pro") {
  return authenticatedApiRequest<SubscriptionCheckout>(token, "/subscriptions", {
    method: "POST",
    body: JSON.stringify({ plan_name: planName }),
  });
}

export async function getSubscriptionStatus(token: string) {
  return authenticatedApiRequest<Entitlement>(token, "/subscriptions/status");
}

export async function cancelSubscription(token: string) {
  return authenticatedApiRequest<{ status: string; access_until: string | null }>(token, "/subscriptions/cancel", { method: "POST" });
}
