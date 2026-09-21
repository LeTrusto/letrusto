import { apiRequest, authenticatedApiRequest } from "@/services/api";

export type Location = {
  id: string;
  name: string;
  slug: string;
  location_type: "CITY" | "ZONE" | "LOCALITY" | string;
  parent_id: string | null;
  city_name: string;
};

export type SellerProfile = {
  id: string;
  user_id: string;
  seller_type: "OWNER" | "AUTHORIZED_REPRESENTATIVE";
  display_name: string;
  phone: string;
  whatsapp_available: boolean;
  email: string | null;
  verification_status: string;
};

export type SellerMedia = {
  id: string;
  media_type: "IMAGE" | "VIDEO" | string;
  storage_key: string;
  public_url: string | null;
  mime_type: string;
  file_size_bytes: number;
  sort_order: number;
  is_cover: boolean;
  caption: string | null;
  status: string;
};

export type SellerProperty = {
  id: string;
  slug: string;
  title: string;
  description: string;
  property_type: "APARTMENT" | "INDEPENDENT_HOUSE" | "VILLA" | "RESIDENTIAL_PLOT" | string;
  price_amount: number | string;
  currency: string;
  built_up_area_sqft: number | string | null;
  carpet_area_sqft: number | string | null;
  plot_area_sqft: number | string | null;
  bhk: number | null;
  floor_number: number | null;
  total_floors: number | null;
  property_age_years?: number | null;
  facing: string | null;
  parking_details: string | null;
  maintenance_amount: number | string | null;
  possession_status: string | null;
  road_width_ft?: number | string | null;
  plot_dimensions: string | null;
  corner_site: boolean | null;
  approval_information?: string | null;
  amenities?: Record<string, boolean> | null;
  address_line: string | null;
  address_visibility: string;
  status: string;
  published_at: string | null;
  created_at?: string;
  updated_at?: string;
  seller_profile_id: string;
  location: Location;
  media: SellerMedia[];
  verification_label: string;
};

export type PropertyPayload = {
  location_id: string;
  title: string;
  description: string;
  property_type: string;
  price_amount: number;
  currency: string;
  built_up_area_sqft?: number;
  carpet_area_sqft?: number;
  plot_area_sqft?: number;
  bhk?: number;
  floor_number?: number;
  total_floors?: number;
  property_age_years?: number;
  facing?: string;
  parking_details?: string;
  maintenance_amount?: number;
  possession_status?: string;
  road_width_ft?: number;
  plot_dimensions?: string;
  corner_site?: boolean;
  approval_information?: string;
  amenities?: Record<string, boolean>;
  address_line?: string;
  address_visibility: string;
};

export type MediaPayload = {
  media_type: "IMAGE" | "VIDEO";
  storage_key: string;
  mime_type: string;
  file_size_bytes: number;
  is_cover: boolean;
  caption?: string;
};

export function getLocations() {
  return apiRequest<Location[]>("/properties/locations");
}

export function getSellerProfile(token: string) {
  return authenticatedApiRequest<SellerProfile>(token, "/seller/profile");
}

export function createSellerProfile(token: string, payload: Omit<SellerProfile, "id" | "user_id" | "verification_status">) {
  return authenticatedApiRequest<SellerProfile>(token, "/seller/profile", { method: "POST", body: JSON.stringify(payload) });
}

export function updateSellerProfile(token: string, payload: Partial<Omit<SellerProfile, "id" | "user_id" | "verification_status">>) {
  return authenticatedApiRequest<SellerProfile>(token, "/seller/profile", { method: "PATCH", body: JSON.stringify(payload) });
}

export function listSellerProperties(token: string) {
  return authenticatedApiRequest<SellerProperty[]>(token, "/seller/properties");
}

export function getSellerProperty(token: string, id: string) {
  return authenticatedApiRequest<SellerProperty>(token, `/seller/properties/${encodeURIComponent(id)}`);
}

export function createSellerProperty(token: string, payload: PropertyPayload) {
  return authenticatedApiRequest<SellerProperty>(token, "/seller/properties", { method: "POST", body: JSON.stringify(payload) });
}

export function updateSellerProperty(token: string, id: string, payload: Partial<PropertyPayload>) {
  return authenticatedApiRequest<SellerProperty>(token, `/seller/properties/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(payload) });
}

export function submitSellerProperty(token: string, id: string) {
  return authenticatedApiRequest<{ id: string; status: string }>(token, `/seller/properties/${encodeURIComponent(id)}/submit`, { method: "POST" });
}

export function addSellerMedia(token: string, id: string, payload: MediaPayload) {
  return authenticatedApiRequest<{ id: string; status: string }>(token, `/seller/properties/${encodeURIComponent(id)}/media`, { method: "POST", body: JSON.stringify(payload) });
}
