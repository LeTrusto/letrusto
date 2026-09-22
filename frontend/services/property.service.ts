import { apiRequest } from "@/services/api";

export type PublicPropertyMedia = {
  id: string;
  media_type: "IMAGE" | "VIDEO" | string;
  public_url: string | null;
  mime_type: string;
  sort_order: number;
  is_cover: boolean;
  caption: string | null;
};

export type PublicProperty = {
  id: string;
  slug: string;
  title: string;
  description: string;
  property_type: string;
  price_amount: number | string;
  currency: string;
  built_up_area_sqft: number | string | null;
  carpet_area_sqft: number | string | null;
  plot_area_sqft: number | string | null;
  bhk: number | null;
  floor_number: number | null;
  total_floors: number | null;
  facing: string | null;
  parking_details: string | null;
  maintenance_amount: number | string | null;
  possession_status: string | null;
  plot_dimensions: string | null;
  corner_site: boolean | null;
  address_visibility: string;
  status: string;
  published_at: string | null;
  location: {
    id: string;
    name: string;
    slug: string;
    location_type: string;
    parent_id: string | null;
    city_name: string;
  };
  media: PublicPropertyMedia[];
  verification_label: string;
};

export type PublicPropertyPage = {
  items: PublicProperty[];
  page: number;
  page_size: number;
  total: number;
  has_more: boolean;
};

export type PublicLocation = {
  id: string;
  name: string;
  slug: string;
  location_type: string;
  parent_id: string | null;
  city_name: string;
};

export type EnquiryPayload = {
  buyer_name: string;
  buyer_phone: string;
  buyer_email?: string;
  whatsapp_available: boolean;
  budget_amount?: number;
  buying_timeline?: string;
  message?: string;
  preferred_contact_method: "PHONE" | "WHATSAPP" | "EMAIL";
  source: "WEBSITE";
  landing_path: string;
  consent_to_share: boolean;
};

export type PublicEnquiryResponse = {
  id: string;
  property_id: string;
  status: string;
  created_at: string;
};

export type PublicPropertyQuery = {
  page?: number;
  page_size?: number;
  type?: string;
  bhk?: number;
  min_price?: number;
  max_price?: number;
  locality?: string;
  search?: string;
  sort?: "newest" | "price_asc" | "price_desc";
};

function queryString(params: PublicPropertyQuery): string {
  const values = Object.entries(params).filter(([, value]) => value !== undefined && value !== "");
  return values.length ? `?${new URLSearchParams(values.map(([key, value]) => [key, String(value)]))}` : "";
}

export async function getPublicProperties(params: PublicPropertyQuery = {}): Promise<PublicPropertyPage> {
  return apiRequest<PublicPropertyPage>(`/properties${queryString(params)}`);
}

export function getPublicLocations(): Promise<PublicLocation[]> {
  return apiRequest<PublicLocation[]>("/locations");
}

export async function getPublicProperty(slug: string): Promise<PublicProperty | null> {
  try {
    return await apiRequest<PublicProperty>(`/properties/${encodeURIComponent(slug)}`);
  } catch {
    return null;
  }
}

export async function createPropertyEnquiry(propertyId: string, payload: EnquiryPayload): Promise<PublicEnquiryResponse> {
  return apiRequest<PublicEnquiryResponse>(`/properties/${encodeURIComponent(propertyId)}/enquiries`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function validateEnquiry(payload: Pick<EnquiryPayload, "buyer_name" | "buyer_phone" | "consent_to_share">): Partial<Record<keyof EnquiryPayload, string>> {
  const errors: Partial<Record<keyof EnquiryPayload, string>> = {};
  if (!payload.buyer_name.trim()) errors.buyer_name = "Please enter your name.";
  if (!payload.buyer_phone.trim()) errors.buyer_phone = "Please enter a phone number.";
  else if (payload.buyer_phone.trim().length < 7) errors.buyer_phone = "Please enter a valid phone number.";
  if (!payload.consent_to_share) errors.consent_to_share = "Consent is required before sending your enquiry.";
  return errors;
}
