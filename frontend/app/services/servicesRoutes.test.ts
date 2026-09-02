import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

function source(path: string) { return readFileSync(fileURLToPath(new URL(path, import.meta.url)), "utf8"); }

describe("service routes", () => {
  it("uses the reusable catalog and existing enquiry endpoint", () => {
    expect(source("./page.tsx")).toContain("ServiceCard");
    expect(source("./[slug]/page.tsx")).toContain("generateStaticParams");
    expect(source("./quote/page.tsx")).toContain("QuoteForm");
    expect(source("../../components/services/QuoteForm.tsx")).toContain("/support/tickets");
    expect(source("../../components/services/QuoteForm.tsx")).toContain('category: "service_enquiry"');
  });
});