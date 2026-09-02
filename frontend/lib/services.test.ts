import { describe, expect, it } from "vitest";
import { SERVICES, getPublishedServices, getServiceBySlug } from "./services";

describe("service catalog", () => {
  it("publishes the initial scoped service set", () => {
    expect(getPublishedServices()).toHaveLength(9);
    expect(getPublishedServices().every((service) => service.status === "published")).toBe(true);
    expect(SERVICES.every((service) => service.included.length > 0 && service.exclusions.length > 0)).toBe(true);
  });

  it("resolves valid routes and rejects unknown routes", () => {
    expect(getServiceBySlug("website-setup")?.name).toBe("Website Setup");
    expect(getServiceBySlug("missing-service")).toBeUndefined();
  });
});