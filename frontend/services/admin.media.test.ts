import { beforeEach, describe, expect, it, vi } from "vitest";

import { getAdminProperty } from "@/services/admin.service";

describe("admin media inspection contract", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("preserves media preview, cover, ordering, type, and lifecycle metadata", async () => {
    const property = { id: "property-1", media: [{ id: "media-1", public_url: "https://cdn.example/media.jpg", media_type: "IMAGE", is_cover: true, sort_order: 0, status: "READY", caption: "Front" }] };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(property), { status: 200 })));
    await expect(getAdminProperty("token", "property-1")).resolves.toMatchObject(property);
  });
});
