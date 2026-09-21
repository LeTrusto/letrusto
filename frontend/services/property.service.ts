import { apiRequest, authenticatedApiRequest } from "@/services/api";

export type PropertyType = "flat" | "plot" | "house";

export type PropertyListing = {
	id: string;
	property_type: PropertyType;
	title: string;
	description: string;
	locality: string;
	city: string;
	price: string;
	area_sqft: string | null;
	bedrooms: number | null;
	image_urls: string[];
	status: string;
	is_featured: boolean;
	is_own_listing: boolean;
	contact_unlocked: boolean;
	contact_name: string | null;
	contact_phone: string | null;
	contact_email: string | null;
	created_at: string;
};

export type PropertyListingPage = {
	items: PropertyListing[];
	total: number;
	page: number;
	page_size: number;
};

export type PropertyPaymentOrder = {
	attempt_id: string;
	listing_id: string;
	purpose: "LISTING_FEE" | "CONTACT_UNLOCK";
	provider: "RAZORPAY";
	key_id: string;
	razorpay_order_id: string;
	amount: number;
	currency: string;
};

export type PropertyPaymentVerification = {
	razorpay_order_id: string;
	razorpay_payment_id: string;
	razorpay_signature: string;
};

export type PropertyListingCreatePayload = {
	property_type: PropertyType;
	title: string;
	description: string;
	locality: string;
	price: number;
	area_sqft?: number;
	bedrooms?: number;
	image_urls: string[];
	contact_name: string;
	contact_phone: string;
	contact_email?: string;
};

export type PropertyFilters = {
	property_type?: PropertyType;
	locality?: string;
	min_price?: number;
	max_price?: number;
	page?: number;
	page_size?: number;
};

export function listProperties(filters: PropertyFilters = {}) {
	const params = new URLSearchParams();
	for (const [key, value] of Object.entries(filters)) {
		if (value !== undefined && value !== "") params.set(key, String(value));
	}
	const query = params.toString();
	return apiRequest<PropertyListingPage>(`/properties${query ? `?${query}` : ""}`);
}

export function getProperty(id: string, token?: string) {
	if (token) return authenticatedApiRequest<PropertyListing>(token, `/properties/${id}`);
	return apiRequest<PropertyListing>(`/properties/${id}`);
}

export function createProperty(token: string, payload: PropertyListingCreatePayload) {
	return authenticatedApiRequest<PropertyPaymentOrder>(token, "/properties", { method: "POST", body: JSON.stringify(payload) });
}

export function verifyListingPayment(token: string, listingId: string, payload: PropertyPaymentVerification) {
	return authenticatedApiRequest<PropertyListing>(token, `/properties/${listingId}/listing-payment/verify`, { method: "POST", body: JSON.stringify(payload) });
}

export function requestContactUnlock(token: string, listingId: string) {
	return authenticatedApiRequest<PropertyPaymentOrder>(token, `/properties/${listingId}/unlock`, { method: "POST" });
}

export function verifyContactUnlock(token: string, listingId: string, payload: PropertyPaymentVerification) {
	return authenticatedApiRequest<PropertyListing>(token, `/properties/${listingId}/unlock/verify`, { method: "POST", body: JSON.stringify(payload) });
}

export function listMyProperties(token: string) {
	return authenticatedApiRequest<PropertyListing[]>(token, "/properties/mine");
}
