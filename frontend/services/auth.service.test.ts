import { beforeEach, describe, expect, it, vi } from "vitest";

import { confirmEmailVerification, loginUser } from "@/services/auth.service";

describe("customer authentication service", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("confirms an email verification token", async () => {
    const result = { message: "Your email has been verified." };
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(result), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(confirmEmailVerification("verification-token-value")).resolves.toEqual(result);
    expect(fetchMock.mock.calls[0][0]).toContain("/auth/email-verification/confirm");
    expect(fetchMock.mock.calls[0][1]).toMatchObject({ body: JSON.stringify({ token: "verification-token-value" }) });
  });

  it("keeps the existing email/password login endpoint", async () => {
    const auth = { access_token: "access", refresh_token: "refresh", token_type: "bearer", expires_in: 900, user_id: "user-1", email: "customer@example.com", full_name: "Customer", role: "user", avatar_url: null };
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(auth), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await loginUser({ email: "customer@example.com", password: "correct-password" });
    expect(fetchMock.mock.calls[0][0]).toContain("/auth/login");
    expect(fetchMock.mock.calls[0][1]).toMatchObject({ body: JSON.stringify({ email: "customer@example.com", password: "correct-password" }) });
  });
});
