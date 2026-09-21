import { beforeEach, describe, expect, it, vi } from "vitest";

import { createPropertyEnquiry, getPublicProperty, validateEnquiry } from "@/services/property.service";

const propertySlug = "the-bougainvillea-house-jayanagar";

describe("public property service", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("loads the public property contract and does not expose seller fields", async () => {
    const result = { id: "property-1", slug: propertySlug, title: "The Bougainvillea House" };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(result), { status: 200 })));
    await expect(getPublicProperty(propertySlug)).resolves.toMatchObject(result);
    const property = await getPublicProperty(propertySlug);
    expect(property).not.toHaveProperty("seller_profile");
    expect(property).not.toHaveProperty("seller_phone");
  });

  it("uses the isolated mock fallback when the public API is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    await expect(getPublicProperty(propertySlug)).resolves.toMatchObject({ slug: propertySlug, status: "LIVE", location: { name: "Jayanagar" } });
    await expect(getPublicProperty("not-a-live-property")).resolves.toBeNull();
  });

  it("requires name, phone, and explicit consent", () => {
    expect(validateEnquiry({ buyer_name: "", buyer_phone: "123", consent_to_share: false })).toEqual({
      buyer_name: "Please enter your name.",
      buyer_phone: "Please enter a valid phone number.",
      consent_to_share: "Consent is required before sending your enquiry.",
    });
    expect(validateEnquiry({ buyer_name: "Asha", buyer_phone: "9876543210", consent_to_share: true })).toEqual({});
  });

  it("posts supported enquiry fields to the public endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ id: "enquiry-1", status: "NEW" }), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    await createPropertyEnquiry("property-1", {
      buyer_name: "Asha Rao",
      buyer_phone: "9876543210",
      whatsapp_available: true,
      preferred_contact_method: "PHONE",
      source: "WEBSITE",
      landing_path: "/properties/example",
      consent_to_share: true,
    });
    expect(fetchMock.mock.calls[0][0]).toContain("/properties/property-1/enquiries");
    expect(fetchMock.mock.calls[0][1]).toMatchObject({ method: "POST", body: expect.stringContaining('"consent_to_share":true') });
  });

  it("surfaces an API failure for the form to recover from", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("bad gateway", { status: 502, statusText: "Bad Gateway" })));
    await expect(createPropertyEnquiry("property-1", {
      buyer_name: "Asha Rao",
      buyer_phone: "9876543210",
      whatsapp_available: false,
      preferred_contact_method: "PHONE",
      source: "WEBSITE",
      landing_path: "/properties/example",
      consent_to_share: true,
    })).rejects.toThrow("API request failed");
  });
});
