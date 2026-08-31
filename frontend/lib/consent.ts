export const CONSENT_STORAGE_KEY = "letrusto:cookie-consent";
export const CONSENT_VERSION = 1;

export type ConsentState = {
  version: number;
  status: "granted";
  essential: true;
  analytics: boolean;
  marketing: boolean;
  updatedAt: string;
};

const listeners = new Set<() => void>();

export function getConsent(): ConsentState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(CONSENT_STORAGE_KEY);
    if (!raw) return null;
    const value = JSON.parse(raw) as Partial<ConsentState>;
    if (value.version !== CONSENT_VERSION || value.status !== "granted" || value.essential !== true) return null;
    if (typeof value.analytics !== "boolean" || typeof value.marketing !== "boolean") return null;
    return value as ConsentState;
  } catch {
    return null;
  }
}

export function saveConsent(analytics: boolean, marketing: boolean): ConsentState {
  const state: ConsentState = {
    version: CONSENT_VERSION,
    status: "granted",
    essential: true,
    analytics,
    marketing,
    updatedAt: new Date().toISOString(),
  };
  window.localStorage.setItem(CONSENT_STORAGE_KEY, JSON.stringify(state));
  if (!analytics) clearAnalyticsIdentifiers();
  listeners.forEach((listener) => listener());
  return state;
}

export function clearAnalyticsIdentifiers(): void {
  if (typeof document === "undefined") return;
  document.cookie.split(";").forEach((entry) => {
    const name = entry.split("=", 1)[0]?.trim();
    if (name && (/^_ga(?:$|_)/.test(name) || /^_gid$/.test(name) || /^_gat(?:$|_)/.test(name))) {
      document.cookie = `${name}=; Max-Age=0; path=/`;
    }
  });
}

export function subscribeToConsent(listener: () => void): () => void {
  listeners.add(listener);
  if (typeof window === "undefined") return () => listeners.delete(listener);
  const handleStorage = (event: StorageEvent) => {
    if (event.key === CONSENT_STORAGE_KEY) listener();
  };
  window.addEventListener("storage", handleStorage);
  return () => {
    listeners.delete(listener);
    window.removeEventListener("storage", handleStorage);
  };
}

export function notifyConsentChanged(): void {
  listeners.forEach((listener) => listener());
}
