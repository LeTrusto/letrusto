import { beforeEach, describe, expect, it, vi } from "vitest";

import { loginUser, requestOtp, verifyOtp } from "@/services/auth.service";

describe("customer authentication service", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("requests an OTP without exposing a code", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ message: "OTP sent" }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const result = await requestOtp({ mobile_number: "9876543210" });
    expect(result).toEqual({ message: "OTP sent" });
    expect(fetchMock.mock.calls[0][1]).toMatchObject({ method: "POST", body: JSON.stringify({ mobile_number: "9876543210" }) });
  });

  it("verifies OTP through the shared auth response", async () => {
    const auth = { access_token: "access", refresh_token: "refresh", token_type: "bearer", expires_in: 900, user_id: "user-1", email: null, full_name: "", role: "user", avatar_url: null };
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(auth), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(verifyOtp({ mobile_number: "9876543210", otp: "123456" })).resolves.toEqual(auth);
    expect(fetchMock.mock.calls[0][0]).toContain("/auth/otp/verify");
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
