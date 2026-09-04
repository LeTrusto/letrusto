import { refreshAccessToken } from "@/services/auth.service";
import type { AuthResponse } from "@/types/auth";

export const ACCESS_TOKEN_KEY = "lt_access_token";
export const REFRESH_TOKEN_KEY = "lt_refresh_token";

const SYNC_KEY = "lt_auth_sync";
const REFRESH_LOCK_KEY = "lt_auth_refresh_lock";
const LOCK_TTL_MS = 10_000;
const WAIT_TIMEOUT_MS = 12_000;

type AuthEvent =
  | { type: "session"; response: AuthResponse; timestamp: number }
  | { type: "logout"; timestamp: number };

type RefreshLock = { owner: string; expiresAt: number };

function readLock(): RefreshLock | null {
  const raw = localStorage.getItem(REFRESH_LOCK_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as RefreshLock;
  } catch {
    return null;
  }
}

function readRecentSession(previousRefreshToken: string, startedAt: number): AuthResponse | null {
  const raw = localStorage.getItem(SYNC_KEY);
  if (!raw) return null;
  try {
    const message = JSON.parse(raw) as AuthEvent;
    const currentRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (
      message.type === "session" &&
      message.response.refresh_token !== previousRefreshToken &&
      (message.timestamp >= startedAt || message.response.refresh_token === currentRefreshToken)
    ) {
      return message.response;
    }
  } catch {
    // Ignore malformed cross-tab messages.
  }
  return null;
}

function wait(milliseconds: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function waitForSession(previousRefreshToken: string, startedAt: number): Promise<AuthResponse | null> {
  return new Promise((resolve) => {
    let settled = false;
    const finish = (response: AuthResponse | null) => {
      if (settled) return;
      settled = true;
      window.removeEventListener("storage", onStorage);
      window.clearTimeout(timeout);
      resolve(response);
    };
    const onStorage = (event: StorageEvent) => {
      if (event.key !== SYNC_KEY || !event.newValue) return;
      finish(readRecentSession(previousRefreshToken, startedAt));
    };
    const timeout = window.setTimeout(() => finish(null), WAIT_TIMEOUT_MS);
    window.addEventListener("storage", onStorage);
  });
}

export function publishAuthSession(response: AuthResponse): void {
  localStorage.setItem(SYNC_KEY, JSON.stringify({ type: "session", response, timestamp: Date.now() } satisfies AuthEvent));
}

export function publishLogout(): void {
  localStorage.setItem(SYNC_KEY, JSON.stringify({ type: "logout", timestamp: Date.now() } satisfies AuthEvent));
}

export function subscribeToAuthEvents(onSession: (response: AuthResponse) => void, onLogout: () => void): () => void {
  const onStorage = (event: StorageEvent) => {
    if (event.key !== SYNC_KEY || !event.newValue) return;
    try {
      const message = JSON.parse(event.newValue) as AuthEvent;
      if (message.type === "session") onSession(message.response);
      if (message.type === "logout") onLogout();
    } catch {
      // Ignore malformed cross-tab messages.
    }
  };
  window.addEventListener("storage", onStorage);
  return () => window.removeEventListener("storage", onStorage);
}

export async function refreshSessionAcrossTabs(refreshToken: string): Promise<AuthResponse> {
  const startedAt = Date.now();
  const syncedSession = waitForSession(refreshToken, startedAt);
  const owner = crypto.randomUUID();
  const deadline = startedAt + WAIT_TIMEOUT_MS;

  while (Date.now() < deadline) {
    const currentRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (currentRefreshToken && currentRefreshToken !== refreshToken) {
      const recentSession = readRecentSession(refreshToken, startedAt);
      if (recentSession) return recentSession;
      const response = await syncedSession;
      if (response) return response;
    }

    const currentLock = readLock();
    if (!currentLock || currentLock.expiresAt <= Date.now()) {
      const lock = { owner, expiresAt: Date.now() + LOCK_TTL_MS } satisfies RefreshLock;
      localStorage.setItem(REFRESH_LOCK_KEY, JSON.stringify(lock));
      if (readLock()?.owner === owner) {
        try {
          const latestRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY) ?? refreshToken;
          if (latestRefreshToken !== refreshToken) {
            const recentSession = readRecentSession(refreshToken, startedAt);
            if (recentSession) return recentSession;
            const response = await syncedSession;
            if (response) return response;
          }
          const response = await refreshAccessToken(latestRefreshToken);
          localStorage.setItem(ACCESS_TOKEN_KEY, response.access_token);
          localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
          publishAuthSession(response);
          return response;
        } finally {
          if (readLock()?.owner === owner) localStorage.removeItem(REFRESH_LOCK_KEY);
        }
      }
    }

    const response = await syncedSession;
    if (response) return response;
    await wait(50);
  }

  throw new Error("Session refresh timed out");
}