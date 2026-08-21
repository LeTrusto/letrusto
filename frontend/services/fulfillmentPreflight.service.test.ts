import { describe, expect, it, vi } from "vitest";

import { runFulfillmentPreflight } from "@/services/fulfillmentPreflight.service";

describe("fulfillment preflight service", () => {
	it("uses the authenticated read-only endpoint and query options", async () => {
		const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ fulfillable: true }), { status: 200 }));
		vi.stubGlobal("fetch", fetchMock);

		await runFulfillmentPreflight("access-token", {
			productId: "product-1",
			variantId: "variant-1",
			quantity: 1,
			destination: "IN",
			logisticsName: "CJPacket Eub",
			storageId: "1",
		});

		expect(fetchMock).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/supplier-validation/preflight/product-1/variant-1?quantity=1&destination=IN&logistics_name=CJPacket+Eub&storage_id=1"),
			expect.objectContaining({ headers: expect.objectContaining({ Authorization: "Bearer access-token" }) }),
		);
		expect(fetchMock.mock.calls[0][1]).not.toHaveProperty("method");
	});
});