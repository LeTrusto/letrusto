import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { PropertyCard } from "@/components/property/PropertyCard";
import { PropertyDetail, PropertyUnavailable } from "@/components/property/PropertyDetail";
import type { PublicProperty } from "@/services/property.service";
import type { MockProperty } from "@/lib/propertyMockData";

const property: PublicProperty = {
  id: "property-1",
  slug: "the-bougainvillea-house-jayanagar",
  title: "The Bougainvillea House",
  description: "A quiet courtyard home wrapped in afternoon light.",
  property_type: "INDEPENDENT_HOUSE",
  price_amount: 38500000,
  currency: "INR",
  built_up_area_sqft: 2460,
  carpet_area_sqft: null,
  plot_area_sqft: null,
  bhk: 4,
  floor_number: null,
  total_floors: null,
  facing: "East",
  parking_details: "2 covered",
  maintenance_amount: null,
  possession_status: "READY",
  plot_dimensions: null,
  corner_site: null,
  address_visibility: "LOCALITY_ONLY",
  status: "LIVE",
  published_at: null,
  location: { id: "location-1", name: "Jayanagar", slug: "jayanagar", location_type: "LOCALITY", parent_id: null, city_name: "Bengaluru" },
  media: [{ id: "media-1", media_type: "IMAGE", public_url: "https://images.unsplash.com/example", mime_type: "image/jpeg", sort_order: 0, is_cover: true, caption: "Courtyard" }],
  verification_label: "CONTACT_VERIFIED",
};

const mockProperty: MockProperty = {
  slug: property.slug,
  title: property.title,
  type: "House",
  locality: "Jayanagar",
  region: "South Bangalore",
  price: "₹3.85 Cr",
  area: "2,460 sq.ft",
  bhk: "4 BHK",
  image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c",
  description: property.description,
  badge: "Editor's pick",
  accent: "terracotta",
};

describe("property detail experience", () => {
  it("renders public property information and the enquiry CTA", () => {
    const html = renderToStaticMarkup(<PropertyDetail property={property} />);
    expect(html).toContain("The Bougainvillea House");
    expect(html).toContain("Jayanagar");
    expect(html).toContain("4 BHK");
    expect(html).toContain("Get Details");
    expect(html).toContain("Courtyard");
    expect(html).not.toContain("seller_profile");
    expect(html).not.toContain("seller_phone");
  });

  it("renders the unavailable public state", () => {
    const html = renderToStaticMarkup(<PropertyUnavailable />);
    expect(html).toContain("This property is");
    expect(html).toContain("no longer available");
    expect(html).toContain("/properties");
  });

  it("links collection cards to the stable property slug", () => {
    const html = renderToStaticMarkup(<PropertyCard property={mockProperty} />);
    expect(html).toContain(`/properties/${property.slug}`);
  });
});
