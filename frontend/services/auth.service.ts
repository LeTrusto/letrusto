import { API_BASE_URL } from "@/services/api";
import type { AuthResponse, LoginPayload, RegisterPayload } from "@/types/auth";

const AUTH_BASE = `${API_BASE_URL}/api/v1/auth`;

export async function registerUser(payload: RegisterPayload): Promise<AuthResponse> {
  let res: Response;
  try {
    res = await fetch(`${AUTH_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("Cannot reach the server. Make sure the backend is running on http://127.0.0.1:8000");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? "Registration failed");
  }
  return (await res.json()) as AuthResponse;
}

export async function loginUser(payload: LoginPayload): Promise<AuthResponse> {
  let res: Response;
  try {
    res = await fetch(`${AUTH_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("Cannot reach the server. Make sure the backend is running on http://127.0.0.1:8000");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? "Login failed");
  }
  return (await res.json()) as AuthResponse;
}

export async function refreshAccessToken(refreshToken: string): Promise<AuthResponse> {
  const res = await fetch(`${AUTH_BASE}/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!res.ok) throw new Error("Session expired");
  return (await res.json()) as AuthResponse;
}

export async function logoutUser(refreshToken: string): Promise<void> {
  await fetch(`${AUTH_BASE}/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  }).catch(() => {});
}
