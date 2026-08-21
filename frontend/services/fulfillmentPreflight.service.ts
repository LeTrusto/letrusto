import { authenticatedApiRequest, buildQueryString } from "@/services/api";

export type FulfillmentPreflight = {
	fulfillable: boolean;
	vid: string;
	product_id: string;
	variant_id: string;
	origin_country: string | null;
	warehouse_id: string | null;
	warehouse_name: string | null;
	sellable_inventory: number;
	requested_quantity: number;
	logistic_name: string | null;
	shipping_cost: number | null;
	delivery_estimate: string | null;
	reason: string | null;
	error_classification: string | null;
	checked_at: string;
};

export type FulfillmentPreflightRequest = {
	productId: string;
	variantId: string;
	quantity: number;
	destination: string;
	logisticsName?: string;
	storageId?: string;
};

export function runFulfillmentPreflight(
	accessToken: string,
	request: FulfillmentPreflightRequest,
) {
	const query = buildQueryString({
		quantity: request.quantity,
		destination: request.destination,
		logistics_name: request.logisticsName,
		storage_id: request.storageId,
	});
	return authenticatedApiRequest<FulfillmentPreflight>(
		accessToken,
		`/supplier-validation/preflight/${encodeURIComponent(request.productId)}/${encodeURIComponent(request.variantId)}${query}`,
	);
}