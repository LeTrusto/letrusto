import { apiRequest } from "@/services/api";
import { properties as mockProperties } from "@/lib/propertyMockData";

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

function fallbackId(slug: string): string {
  let hash = 0;
  for (const character of slug) hash = (hash * 31 + character.charCodeAt(0)) >>> 0;
  return `00000000-0000-4000-8000-${hash.toString(16).padStart(12, "0")}`;
}

function fallbackProperty(slug: string): PublicProperty | null {
  const property = mockProperties.find((item) => item.slug === slug);
  if (!property) return null;

  const propertyType = {
    Apartment: "APARTMENT",
    Villa: "VILLA",
    House: "INDEPENDENT_HOUSE",
    Plot: "RESIDENTIAL_PLOT",
  }[property.type];

  return {
    id: fallbackId(slug),
    slug: property.slug,
    title: property.title,
    description: property.description,
    property_type: propertyType,
    price_amount: Number(property.price.replace(/[^0-9.]/g, "")) * (property.price.includes("Cr") ? 10000000 : 100000),
    currency: "INR",
    built_up_area_sqft: Number(property.area.replace(/[^0-9.]/g, "")),
    carpet_area_sqft: null,
    plot_area_sqft: property.type === "Plot" ? Number(property.area.replace(/[^0-9.]/g, "")) : null,
    bhk: property.bhk ? Number(property.bhk.replace(/[^0-9]/g, "")) : null,
    floor_number: null,
    total_floors: null,
    facing: null,
    parking_details: null,
    maintenance_amount: null,
    possession_status: null,
    plot_dimensions: null,
    corner_site: null,
    address_visibility: "LOCALITY_ONLY",
    status: "LIVE",
    published_at: null,
    location: {
      id: fallbackId(`${slug}-location`),
      name: property.locality,
      slug: property.locality.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
      location_type: "LOCALITY",
      parent_id: null,
      city_name: "Bengaluru",
    },
    media: [
      {
        id: fallbackId(`${slug}-media`),
        media_type: "IMAGE",
        public_url: property.image,
        mime_type: "image/jpeg",
        sort_order: 0,
        is_cover: true,
        caption: property.title,
      },
      ...(property.secondaryImage
        ? [{
            id: fallbackId(`${slug}-secondary`),
            media_type: "IMAGE" as const,
            public_url: property.secondaryImage,
            mime_type: "image/jpeg",
            sort_order: 1,
            is_cover: false,
            caption: `${property.title} interior`,
          }]
        : []),
    ],
    verification_label: "NOT_REVIEWED",
  };
}

export async function getPublicProperty(slug: string): Promise<PublicProperty | null> {
  try {
    return await apiRequest<PublicProperty>(`/properties/${encodeURIComponent(slug)}`);
  } catch {
    return process.env.NODE_ENV === "production" ? null : fallbackProperty(slug);
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
