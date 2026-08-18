import { buildApiUrl } from "@/services/api";
import type { CustomerAccount } from "@/types/account";

async function accountRequest<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildApiUrl(path), {
    ...init,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}`, ...(init?.headers ?? {}) },
  });
  if (!response.ok) throw new Error("Unable to load account");
  return (await response.json()) as T;
}

export function getAccount(token: string) {
  return accountRequest<CustomerAccount>("/account", token);
}

export function updateAccountProfile(token: string, fullName: string) {
  return accountRequest<CustomerAccount>("/account/profile", token, {
    method: "PATCH",
    body: JSON.stringify({ full_name: fullName }),
  });
}