import { apiRequest, authenticatedApiRequest } from "@/services/api";
import type { PublicVerification } from "@/utils/verification";

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
  verification: PublicVerification;
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
  mime_type: string;
  file_size_bytes: number;
  is_cover: boolean;
  caption?: string;
};

export type MediaUploadTarget = {
  media_id: string;
  upload_url: string;
  headers: Record<string, string>;
  expires_at: string;
  status: string;
};

export type SellerEnquiryHistory = {
  old_status: string | null;
  new_status: string;
  note: string | null;
  created_at: string;
};

export type SellerEnquiry = {
  id: string;
  property_id: string;
  duplicate_of_id: string | null;
  property_slug: string;
  property_title: string;
  property_type: string;
  locality: string;
  buyer_name: string;
  buyer_phone: string | null;
  buyer_email: string | null;
  whatsapp_available: boolean;
  budget_amount: number | string | null;
  buying_timeline: string | null;
  message: string | null;
  preferred_contact_method: string;
  source: string;
  source_medium: string | null;
  source_content: string | null;
  campaign_id: string | null;
  landing_path: string | null;
  consent_to_share: boolean;
  status: string;
  created_at: string;
  history: SellerEnquiryHistory[];
};

export function getLocations() {
  return apiRequest<Location[]>("/locations");
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

export function requestSellerPropertyChanges(token: string, id: string) {
  return authenticatedApiRequest<{ id: string; status: string }>(token, `/seller/properties/${encodeURIComponent(id)}/request-changes`, { method: "POST" });
}

export function createSellerMediaUploadTarget(token: string, id: string, payload: Omit<MediaPayload, "storage_key">) {
  return authenticatedApiRequest<MediaUploadTarget>(token, `/seller/properties/${encodeURIComponent(id)}/media/upload-target`, { method: "POST", body: JSON.stringify(payload) });
}

export function completeSellerMediaUpload(token: string, propertyId: string, mediaId: string) {
  return authenticatedApiRequest<{ id: string; status: string; public_url: string | null }>(token, `/seller/properties/${encodeURIComponent(propertyId)}/media/${encodeURIComponent(mediaId)}/complete`, { method: "POST" });
}

export function uploadMockSellerMedia(token: string, uploadUrl: string, content: Blob, contentType: string) {
  if (uploadUrl.startsWith("mock://")) {
    const path = `/seller/media/mock-upload/${uploadUrl.slice("mock://".length)}`;
    return authenticatedApiRequest<void>(token, path, { method: "PUT", headers: { "Content-Type": contentType }, body: content });
  }

  return fetch(uploadUrl, {
    method: "PUT",
    headers: { "Content-Type": contentType },
    body: content,
  }).then((response) => {
    if (!response.ok) throw new Error(`Media upload failed (${response.status})`);
  });
}

export function deleteSellerMedia(token: string, propertyId: string, mediaId: string) {
  return authenticatedApiRequest<void>(token, `/seller/properties/${encodeURIComponent(propertyId)}/media/${encodeURIComponent(mediaId)}`, { method: "DELETE" });
}

export function listSellerEnquiries(token: string) {
  return authenticatedApiRequest<SellerEnquiry[]>(token, "/seller/enquiries");
}

export function listSellerPropertyEnquiries(token: string, propertyId: string) {
  return authenticatedApiRequest<SellerEnquiry[]>(token, `/seller/properties/${encodeURIComponent(propertyId)}/enquiries`);
}

export function getSellerEnquiry(token: string, id: string) {
  return authenticatedApiRequest<SellerEnquiry>(token, `/seller/enquiries/${encodeURIComponent(id)}`);
}

export function updateSellerEnquiryStatus(token: string, id: string, status: string, note?: string) {
  return authenticatedApiRequest<SellerEnquiry>(token, `/seller/enquiries/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify({ status, note }) });
}
