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
let cachedRawValue: string | null | undefined;
let cachedConsent: ConsentState | null = null;

export function getConsent(): ConsentState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(CONSENT_STORAGE_KEY);
    if (raw === cachedRawValue) return cachedConsent;
    cachedRawValue = raw;
    if (!raw) return null;
    const value = JSON.parse(raw) as Partial<ConsentState>;
    if (value.version !== CONSENT_VERSION || value.status !== "granted" || value.essential !== true) {
      cachedConsent = null;
      return cachedConsent;
    }
    if (typeof value.analytics !== "boolean" || typeof value.marketing !== "boolean") {
      cachedConsent = null;
      return cachedConsent;
    }
    cachedConsent = value as ConsentState;
    return cachedConsent;
  } catch {
    cachedRawValue = undefined;
    cachedConsent = null;
    return cachedConsent;
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
  const serialized = JSON.stringify(state);
  window.localStorage.setItem(CONSENT_STORAGE_KEY, serialized);
  cachedRawValue = serialized;
  cachedConsent = state;
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
  document.querySelectorAll('script[src*="googletagmanager.com"], script#ga4-init').forEach((script) => script.remove());
  const browserWindow = window as Window & { gtag?: (...args: unknown[]) => void; dataLayer?: unknown[] };
  browserWindow.gtag = undefined;
  browserWindow.dataLayer = [];
}

export function subscribeToConsent(listener: () => void): () => void {
  listeners.add(listener);
  if (typeof window === "undefined") return () => listeners.delete(listener);
  const handleStorage = (event: StorageEvent) => {
    if (event.key === CONSENT_STORAGE_KEY) {
      cachedRawValue = undefined;
      cachedConsent = null;
      if (!getConsent()?.analytics) clearAnalyticsIdentifiers();
      listener();
    }
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
