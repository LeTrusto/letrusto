import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

function source(path: string) {
  return readFileSync(fileURLToPath(new URL(path, import.meta.url)), "utf8");
}

describe("acquisition route metadata", () => {
  it("keeps the tools index canonical and service titles free of template duplication", () => {
    const tools = source("./tools/page.tsx");
    const services = source("./services/[slug]/page.tsx");
    expect(tools).toContain('canonical: "/tools"');
    expect(services).toContain('replace(/\\s*\\|\\s*LeTrusto$/i, "")');
  });
});