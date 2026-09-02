import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

function source(path: string) {
  return readFileSync(fileURLToPath(new URL(path, import.meta.url)), "utf8");
}

describe("digital product routes", () => {
  it("keeps the catalog and product page in the digital product domain", () => {
    const catalog = source("./page.tsx");
    const detail = source("./[slug]/page.tsx");
    expect(catalog).toContain("DigitalProductCard");
    expect(catalog).toContain("getPublishedDigitalProducts");
    expect(detail).toContain("DigitalProductPurchase");
    expect(detail).toContain("generateStaticParams");
    expect(detail).not.toContain("createOrder");
    expect(detail).not.toContain("Printful");
  });
});