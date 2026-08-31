import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath, URL } from "node:url";

import { describe, expect, it } from "vitest";

function source(path: string) {
  return readFileSync(fileURLToPath(new URL(path, import.meta.url)), "utf8");
}

const routes = [
  "./privacy-policy/page.tsx",
  "./terms-of-use/page.tsx",
  "./shipping-policy/page.tsx",
  "./returns-policy/page.tsx",
  "./cancellation-policy/page.tsx",
  "./support/page.tsx",
];

const footer = source("../components/layout/CommerceFooter.tsx");
const checkout = source("./checkout/page.tsx");
const product = source("./product/[slug]/ProductDetailView.tsx");
const contact = source("./contact/page.tsx");
const sitemap = source("./sitemap.ts");
const robots = source("./robots.ts");
const cookieConsent = source("../components/CookieConsent.tsx");

describe("legal and policy route coverage", () => {
  it("keeps every customer legal route implemented", () => {
    for (const route of routes) {
      expect(existsSync(fileURLToPath(new URL(route, import.meta.url)))).toBe(true);
    }
  });

  it("links all available legal policies from the footer", () => {
    for (const href of ["/privacy-policy", "/terms-of-use", "/shipping-policy", "/returns-policy", "/cancellation-policy"]) {
      expect(footer).toContain(href);
    }
    expect(footer).toContain("Cookie Preferences");
    expect(footer).toContain("/support?tab=contact&category=contact");
  });

  it("keeps cookie preferences reopenable after consent is saved", () => {
    expect(cookieConsent).toContain("letrustoOpenCookiePreferences");
    expect(cookieConsent).toContain("letrusto:open-cookie-preferences");
  });

  it("links all available legal policies from checkout before payment", () => {
    for (const href of ["/privacy-policy", "/terms-of-use", "/shipping-policy", "/returns-policy", "/cancellation-policy"]) {
      expect(checkout).toContain(href);
    }
    expect(checkout).toContain("Razorpay in INR");
    expect(checkout).not.toContain("INR_PER_USD");
    expect(checkout).not.toContain("NEXT_PUBLIC_PRICING_FX_RATE");
  });

  it("links product return copy to the returns policy", () => {
    expect(product).toContain("/returns-policy");
    expect(product).toContain("Made-to-order product");
    expect(product).not.toContain("Returns subject to product policy");
  });

  it("uses support as the canonical customer contact experience", () => {
    expect(contact).toContain('canonical: "/support"');
    expect(contact).toContain('index: false');
    expect(contact).toContain('redirect("/support?tab=contact&category=contact")');
    expect(sitemap).not.toContain("${BASE_URL}/contact");
    expect(sitemap).toContain("${BASE_URL}/support");
  });

  it("exposes legal routes through sitemap and robots without protected auth", () => {
    for (const path of ["/privacy-policy", "/terms-of-use", "/shipping-policy", "/returns-policy", "/cancellation-policy"]) {
      expect(sitemap).toContain(path);
      expect(robots).toContain(path);
    }
    expect(robots).not.toContain('"/contact"');
  });

  it("does not publish active international checkout, GSTIN, or Stripe claims", () => {
    const publicSources = [
      source("./privacy-policy/page.tsx"),
      source("./terms-of-use/page.tsx"),
      source("./shipping-policy/page.tsx"),
      source("./returns-policy/page.tsx"),
      source("./cancellation-policy/page.tsx"),
      footer,
      checkout,
    ].join("\n");
    expect(publicSources).not.toMatch(/GSTIN|GST registered|Stripe checkout|international checkout is available/i);
    expect(publicSources).toContain("International checkout is not available yet");
    expect(publicSources).toContain("Razorpay");
  });
});
