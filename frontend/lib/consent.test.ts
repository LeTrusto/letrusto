import { beforeEach, describe, expect, it, vi } from "vitest";

import { CONSENT_STORAGE_KEY, getConsent, saveConsent } from "@/lib/consent";
import { trackEvent } from "@/lib/analytics";

function installBrowserStorage() {
  const values = new Map<string, string>();
  vi.stubGlobal("window", {
    localStorage: {
      getItem: (key: string) => values.get(key) ?? null,
      setItem: (key: string, value: string) => values.set(key, value),
    },
    location: { href: "https://letrusto.com/" },
    gtag: vi.fn(),
  });
  vi.stubGlobal("document", { title: "LeTrusto", cookie: "", querySelectorAll: () => [] });
}

describe("cookie consent", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    installBrowserStorage();
  });

  it("stores essential, analytics, marketing, version, and timestamp state", () => {
    const state = saveConsent(true, false);
    expect(state).toMatchObject({ version: 1, status: "granted", essential: true, analytics: true, marketing: false });
    expect(state.updatedAt).toEqual(expect.any(String));
    expect(getConsent()).toEqual(state);
  });

  it("stores rejection while keeping essential enabled", () => {
    const state = saveConsent(false, false);
    expect(state).toMatchObject({ status: "granted", essential: true, analytics: false, marketing: false });
  });

  it("rejects old or malformed consent versions", () => {
    window.localStorage.setItem(CONSENT_STORAGE_KEY, JSON.stringify({ version: 0, status: "granted", essential: true, analytics: true, marketing: true }));
    expect(getConsent()).toBeNull();
  });

  it("does not send analytics events without affirmative consent", () => {
    process.env.NODE_ENV = "production";
    trackEvent("checkout_started");
    expect(window.gtag).not.toHaveBeenCalled();
  });

  it("sends analytics events only after analytics consent", () => {
    process.env.NODE_ENV = "production";
    saveConsent(true, false);
    trackEvent("checkout_started", { value: 1 });
    expect(window.gtag).toHaveBeenCalledWith("event", "checkout_started", { value: 1 });
  });
});
