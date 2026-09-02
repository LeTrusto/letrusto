export const GA_MEASUREMENT_ID = "G-J8SC0HRNT2";

export type SafeAnalyticsEvent =
	| "tool_view"
	| "tool_complete"
	| "digital_products_view"
	| "digital_product_view"
	| "digital_product_cta_clicked"
	| "services_view"
	| "service_detail_view"
	| "get_quote_clicked"
	| "quote_form_started"
	| "service_enquiry_submitted"
	| "service_enquiry_failed";

export type SafeAnalyticsParams = Record<string, string>;

const SAFE_PARAMETER_KEYS: Record<SafeAnalyticsEvent, readonly string[]> = {
	tool_view: ["tool_name"],
	tool_complete: ["tool_name"],
	digital_products_view: ["page"],
	digital_product_view: ["product_name", "product_slug"],
	digital_product_cta_clicked: ["product_name", "product_slug", "interaction"],
	services_view: ["page"],
	service_detail_view: ["service_name", "service_slug"],
	get_quote_clicked: ["service_name", "service_slug", "location"],
	quote_form_started: ["service_name", "service_slug"],
	service_enquiry_submitted: ["service_name", "service_slug"],
	service_enquiry_failed: ["service_name", "service_slug", "failure_type"],
};

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

export function trackSafeEvent(event: SafeAnalyticsEvent, params: SafeAnalyticsParams = {}) {
	const allowedKeys = SAFE_PARAMETER_KEYS[event];
	const safeParams = Object.fromEntries(Object.entries(params).filter(([key]) => allowedKeys.includes(key)));
	trackEvent(event, safeParams);
}