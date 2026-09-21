import { buildApiUrl } from "@/services/api";

export type ShippingAddress = {
  line1: string;
  line2?: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
};

export type CustomerAccount = {
  email: string | null;
  full_name: string;
  phone: string | null;
  shipping_address: ShippingAddress | null;
  email_verified: boolean;
  created_at: string;
};

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

export function updateAccountProfile(token: string, profile: { full_name?: string; phone?: string; shipping_address?: ShippingAddress }) {
  return accountRequest<CustomerAccount>("/account/profile", token, {
    method: "PATCH",
    body: JSON.stringify(profile),
  });
}