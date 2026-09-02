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
    const purchase = source("../../components/digital-products/DigitalProductPurchase.tsx");
    const callout = source("../../components/digital-products/DigitalProductCallout.tsx");
    expect(catalog).toContain("DigitalProductCard");
    expect(catalog).toContain("getPublishedDigitalProducts");
    expect(detail).toContain("DigitalProductPurchase");
    expect(purchase).toContain("purchase.status.toLowerCase() === \"verified\"");
    expect(callout).toContain('interaction: "view_product"');
    expect(callout).toContain("source_tool");
    expect(detail).toContain("generateStaticParams");
    expect(detail).not.toContain("createOrder");
    expect(detail).not.toContain("Printful");
  });
});