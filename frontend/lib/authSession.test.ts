import { beforeEach, describe, expect, it, vi } from "vitest";

import type { AuthResponse } from "@/types/auth";

const refreshAccessToken = vi.fn();

vi.mock("@/services/auth.service", () => ({ refreshAccessToken }));

class MemoryStorage {
  private values = new Map<string, string>();

  getItem(key: string) {
    return this.values.get(key) ?? null;
  }

  setItem(key: string, value: string) {
    this.values.set(key, value);
    window.dispatchEvent({ key, newValue: value } as StorageEvent);
  }

  removeItem(key: string) {
    this.values.delete(key);
  }
}

const authResponse = (suffix: string): AuthResponse => ({
  access_token: `access-${suffix}`,
  refresh_token: `refresh-${suffix}`,
  token_type: "bearer",
  expires_in: 900,
  user_id: "user-1",
  email: "user@example.com",
  full_name: "User",
  role: "user",
  avatar_url: null,
});

describe("refreshSessionAcrossTabs", () => {
  beforeEach(() => {
    const listeners = new Map<string, Set<(event: Event) => void>>();
    globalThis.window = {
      addEventListener: (type: string, listener: EventListenerOrEventListenerObject) => {
        const entries = listeners.get(type) ?? new Set();
        entries.add(typeof listener === "function" ? listener : listener.handleEvent.bind(listener));
        listeners.set(type, entries);
      },
      removeEventListener: () => undefined,
      dispatchEvent: (event: Event) => {
        listeners.get("storage")?.forEach((listener) => listener(event));
        return true;
      },
      setTimeout,
      clearTimeout,
    } as unknown as Window & typeof globalThis;
    globalThis.localStorage = new MemoryStorage() as unknown as Storage;
    refreshAccessToken.mockReset();
  });

  it("allows concurrent tabs to share one rotated session", async () => {
    const next = authResponse("new");
    refreshAccessToken.mockImplementation(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10));
      return next;
    });
    localStorage.setItem("lt_refresh_token", "refresh-old");

    const { refreshSessionAcrossTabs } = await import("@/lib/authSession");
    const results = await Promise.all([
      refreshSessionAcrossTabs("refresh-old"),
      refreshSessionAcrossTabs("refresh-old"),
    ]);

    expect(results.map((result) => result.refresh_token)).toEqual(["refresh-new", "refresh-new"]);
    expect(refreshAccessToken).toHaveBeenCalledTimes(1);
  });

  it("adopts a session rotated before a stale tab starts", async () => {
    const next = authResponse("new");
    localStorage.setItem("lt_refresh_token", next.refresh_token);
    localStorage.setItem("lt_auth_sync", JSON.stringify({ type: "session", response: next, timestamp: Date.now() - 1_000 }));

    const { refreshSessionAcrossTabs } = await import("@/lib/authSession");
    const result = await refreshSessionAcrossTabs("refresh-old");

    expect(result).toEqual(next);
    expect(refreshAccessToken).not.toHaveBeenCalled();
  });
});