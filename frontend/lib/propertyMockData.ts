export type PropertyType = "Apartment" | "Villa" | "House" | "Plot";

export type MockProperty = {
  slug: string;
  title: string;
  type: PropertyType;
  locality: string;
  region: string;
  price: string;
  area: string;
  bhk?: string;
  image: string;
  secondaryImage?: string;
  description: string;
  badge: string;
  accent: "terracotta" | "sage" | "amber" | "violet";
};

export const properties: MockProperty[] = [
  {
    slug: "the-bougainvillea-house-jayanagar",
    title: "The Bougainvillea House",
    type: "House",
    locality: "Jayanagar",
    region: "South Bangalore",
    price: "₹3.85 Cr",
    area: "2,460 sq.ft",
    bhk: "4 BHK",
    image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1500&q=85",
    secondaryImage: "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1000&q=85",
    description: "A quiet courtyard home wrapped in afternoon light and old trees.",
    badge: "Editor's pick",
    accent: "terracotta",
  },
  {
    slug: "terrace-light-jp-nagar",
    title: "Terrace Light",
    type: "Apartment",
    locality: "JP Nagar",
    region: "South Bangalore",
    price: "₹1.25 Cr",
    area: "1,458 sq.ft",
    bhk: "3 BHK",
    image: "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1200&q=85",
    description: "Corner apartment with generous windows, a treetop outlook and soft finishes.",
    badge: "Just found",
    accent: "sage",
  },
  {
    slug: "monsoon-court-whitefield",
    title: "Monsoon Court",
    type: "Villa",
    locality: "Whitefield",
    region: "East Bangalore",
    price: "₹2.74 Cr",
    area: "2,980 sq.ft",
    bhk: "4 BHK",
    image: "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=85",
    description: "A garden-facing villa designed for long lunches and slower mornings.",
    badge: "Garden living",
    accent: "amber",
  },
  {
    slug: "the-linen-loft-hebbal",
    title: "The Linen Loft",
    type: "Apartment",
    locality: "Hebbal",
    region: "North Bangalore",
    price: "₹1.88 Cr",
    area: "1,860 sq.ft",
    bhk: "3 BHK",
    image: "https://images.unsplash.com/photo-1600210491892-03d54c0aaf87?auto=format&fit=crop&w=1200&q=85",
    description: "Calm, tactile interiors with the city just beyond the balcony.",
    badge: "Light-filled",
    accent: "violet",
  },
  {
    slug: "canopy-edge-hennur",
    title: "Canopy Edge",
    type: "House",
    locality: "Hennur",
    region: "North Bangalore",
    price: "₹1.62 Cr",
    area: "2,100 sq.ft",
    bhk: "3 BHK",
    image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=85",
    description: "A contemporary home with an instinct for green, shade and space.",
    badge: "New perspective",
    accent: "sage",
  },
  {
    slug: "red-earth-villa-kanakapura",
    title: "Red Earth Villa",
    type: "Villa",
    locality: "Kanakapura Road",
    region: "South Bangalore",
    price: "₹3.1 Cr",
    area: "3,420 sq.ft",
    bhk: "4 BHK",
    image: "https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=1200&q=85",
    description: "A warm, low-slung retreat where architecture meets the landscape.",
    badge: "Room to breathe",
    accent: "terracotta",
  },
  {
    slug: "the-north-star-yelahanka",
    title: "The North Star",
    type: "Plot",
    locality: "Yelahanka",
    region: "North Bangalore",
    price: "₹94 L",
    area: "2,400 sq.ft",
    image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=85",
    description: "A generous, east-facing canvas for the house you have not drawn yet.",
    badge: "Build your own",
    accent: "amber",
  },
  {
    slug: "indigo-court-hoodi",
    title: "Indigo Court",
    type: "Apartment",
    locality: "Hoodi",
    region: "East Bangalore",
    price: "₹1.48 Cr",
    area: "1,640 sq.ft",
    bhk: "3 BHK",
    image: "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1200&q=85",
    description: "A polished city home for people who like their evenings unhurried.",
    badge: "Easy city living",
    accent: "violet",
  },
];

export const categories = [
  { label: "Apartments", note: "High-rise living", type: "Apartment" as const, image: properties[1].image, count: "04" },
  { label: "Villas", note: "Space to breathe", type: "Villa" as const, image: properties[2].image, count: "02" },
  { label: "Houses", note: "A little more yours", type: "House" as const, image: properties[0].image, count: "02" },
  { label: "Plots", note: "Start with possibility", type: "Plot" as const, image: properties[6].image, count: "01" },
];

export const localities = [
  { name: "South Bengaluru", examples: "Jayanagar · JP Nagar · Banashankari", image: properties[0].image },
  { name: "North Bengaluru", examples: "Hebbal · Yelahanka · Hennur", image: properties[3].image },
  { name: "East Bengaluru", examples: "Whitefield · Hoodi · Brookefield", image: properties[2].image },
  { name: "West Bengaluru", examples: "Rajajinagar · Malleshwaram · Vijayanagar", image: properties[5].image },
  { name: "Central Bengaluru", examples: "Indiranagar · Ulsoor · Richmond Town", image: properties[7].image },
  { name: "South-East Bengaluru", examples: "Sarjapur · Bellandur · HSR Layout", image: properties[1].image },
  { name: "Outer Bengaluru", examples: "Kanakapura Road · Devanahalli · Anekal", image: properties[6].image },
];
