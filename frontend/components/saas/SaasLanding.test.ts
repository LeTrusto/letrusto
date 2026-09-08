import { readFileSync } from "node:fs";
import { fileURLToPath, URL } from "node:url";

import { describe, expect, it } from "vitest";

const source = readFileSync(fileURLToPath(new URL("./SaasLanding.tsx", import.meta.url)), "utf8");

describe("SaaS pricing billing contract", () => {
  it("advertises monthly plans only", () => {
    expect(source).toContain('Monthly plans');
    expect(source).toContain('monthly: 999');
    expect(source).toContain('monthly: 2499');
    expect(source).not.toMatch(/annual|yearly|save 20%/i);
  });
});
