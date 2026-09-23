import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import NotificationCenter, { notificationTarget } from "@/components/notifications/NotificationCenter";
import { AuthProvider } from "@/lib/authContext";

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));

beforeEach(() => { vi.restoreAllMocks(); });

const notification = (type: string, id = "property-1") => ({ id: 1, type, title: "Update", body: "A privacy-safe update.", is_read: false, created_at: "2026-09-23T10:00:00Z", related_entity_type: type, related_entity_id: id });

describe("NotificationCenter", () => {
  it("maps server related entities to existing role-specific destinations", () => {
    expect(notificationTarget(notification("PROPERTY"), false)).toBe("/seller/properties/property-1");
    expect(notificationTarget(notification("PROPERTY"), true)).toBe("/admin/properties/property-1");
    expect(notificationTarget(notification("ENQUIRY", "enquiry-1"), false)).toBe("/seller/leads/enquiry-1");
    expect(notificationTarget(notification("ENQUIRY", "enquiry-1"), true)).toBe("/admin/enquiries");
  });

  it("renders a private notification trigger without exposing notification data initially", () => {
    const html = renderToStaticMarkup(<AuthProvider><NotificationCenter /></AuthProvider>);
    expect(html).toContain("Notifications");
    expect(html).not.toContain("A privacy-safe update.");
  });
});