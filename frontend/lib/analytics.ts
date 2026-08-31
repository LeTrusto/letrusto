export const GA_MEASUREMENT_ID = "G-J8SC0HRNT2";

declare global {
	interface Window {
		dataLayer: unknown[];
		gtag?: (...args: unknown[]) => void;
	}
}

export function isAnalyticsEnabled() {
	return process.env.NODE_ENV === "production" && typeof window !== "undefined";
}

function hasAnalyticsConsent() {
	if (!isAnalyticsEnabled()) return false;
	try {
		const raw = window.localStorage.getItem("letrusto:cookie-consent");
		const consent = raw ? JSON.parse(raw) as { version?: number; status?: string; essential?: boolean; analytics?: boolean } : null;
		return consent?.version === 1 && consent.status === "granted" && consent.essential === true && consent.analytics === true;
	} catch {
		return false;
	}
}

export function trackPageView(url: string) {
	if (!hasAnalyticsConsent() || typeof window.gtag !== "function") {
		return;
	}

	window.gtag("event", "page_view", {
		page_path: url,
		page_location: window.location.href,
		page_title: document.title,
	});
}

export function trackEvent(action: string, params?: Record<string, string | number | boolean>) {
	if (!hasAnalyticsConsent() || typeof window.gtag !== "function") {
		return;
	}

	window.gtag("event", action, params ?? {});
}