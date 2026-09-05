import { apiRequest } from "@/services/api";

export type WidgetQuizLead = {
  email: string;
  full_name?: string;
  business_type: string;
  primary_goal: string;
  monthly_visitors: string;
  recommended_widget: string;
  source?: string;
  consented_to_updates: boolean;
};

export async function captureWidgetQuizLead(lead: WidgetQuizLead) {
  return apiRequest<{ message: string; recommended_widget: string }>("/marketing/leads", {
    method: "POST",
    body: JSON.stringify(lead),
  });
}

export async function recordMarketingEvent(eventType: string, payload: Record<string, string>) {
  return apiRequest<{ message: string }>("/analytics/events", {
    method: "POST",
    body: JSON.stringify({ event_type: eventType, session_id: getMarketingSessionId(), payload }),
  });
}

function getMarketingSessionId() {
  if (typeof window === "undefined") return undefined;
  const key = "letrusto:marketing-session";
  const existing = window.sessionStorage.getItem(key);
  if (existing) return existing;
  const created = crypto.randomUUID();
  window.sessionStorage.setItem(key, created);
  return created;
}
