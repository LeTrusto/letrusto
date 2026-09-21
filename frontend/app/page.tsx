import type { Metadata } from "next";
import { PropertyExperience } from "@/components/property/PropertyExperience";

export const metadata: Metadata = {
  title: { absolute: "Bangalore properties, discovered differently." },
  description: "A considered way to discover homes, plots and spaces shaping Bangalore.",
  alternates: { canonical: "/" },
  openGraph: {
    title: "Bangalore properties, discovered differently.",
    description: "A considered way to discover homes, plots and spaces shaping Bangalore.",
    url: "/",
    siteName: "Bangalore property journal",
    type: "website",
  },
};

export default function Home() {
  return <PropertyExperience />;
}

