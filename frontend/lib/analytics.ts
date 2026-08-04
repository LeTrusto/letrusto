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

export function trackPageView(url: string) {
	if (!isAnalyticsEnabled() || typeof window.gtag !== "function") {
		return;
	}

	window.gtag("event", "page_view", {
		page_path: url,
		page_location: window.location.href,
		page_title: document.title,
	});
}

export function trackEvent(action: string, params?: Record<string, string | number | boolean>) {
	if (!isAnalyticsEnabled() || typeof window.gtag !== "function") {
		return;
	}

	window.gtag("event", action, params ?? {});
}