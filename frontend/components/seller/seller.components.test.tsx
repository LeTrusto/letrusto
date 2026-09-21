import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import SellerStatus, { statusLabel } from "@/components/seller/SellerStatus";

describe("seller status presentation", () => {
  it("maps backend lifecycle values to friendly labels", () => {
    expect(statusLabel("DRAFT")).toBe("Draft");
    expect(statusLabel("UNDER_REVIEW")).toBe("Under Review");
    expect(statusLabel("CHANGES_REQUESTED")).toBe("Changes Requested");
    expect(statusLabel("LIVE")).toBe("Live");
  });

  it("renders an accessible status value without exposing private fields", () => {
    const html = renderToStaticMarkup(<SellerStatus status="UNDER_REVIEW" />);
    expect(html).toContain("Under Review");
    expect(html).not.toContain("seller_profile");
    expect(html).not.toContain("storage_key");
  });
});
