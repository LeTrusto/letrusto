import { beforeEach, describe, expect, it, vi } from "vitest";

import { deleteSellerMedia, uploadMockSellerMedia } from "@/services/seller.service";

describe("seller media service", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("uploads development mock media through the authenticated API route", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ status: "uploaded" }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await uploadMockSellerMedia("token", "mock://properties/p/media/1/original", new Blob(["data"]), "image/png");
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/seller/media/mock-upload/properties/p/media/1/original"), expect.objectContaining({ method: "PUT", body: expect.any(Blob) }));
  });

  it("surfaces upload failures for the editor to handle", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Upload failed" }), { status: 400 })));
    await expect(uploadMockSellerMedia("token", "mock://properties/p/media/1/original", new Blob(["data"]), "image/png")).rejects.toThrow("Upload failed");
  });

  it("calls the seller-owned media delete endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({}), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await deleteSellerMedia("token", "property-1", "media-1");
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/seller/properties/property-1/media/media-1"), expect.objectContaining({ method: "DELETE" }));
  });
});
