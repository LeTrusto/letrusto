import type { Metadata } from "next";

import SaaSLanding from "@/components/saas/SaasLanding";

export const metadata: Metadata = {
  title: "Social Proof Widgets for Growing Businesses",
  description: "Make customer trust visible with lightweight social proof and review widgets from LeTrusto.",
  alternates: { canonical: "/" },
  openGraph: {
    title: "LeTrusto — Social proof, made visible",
    description: "Lightweight sales popups, Wall of Love grids, and review collection for ambitious businesses.",
    url: "/",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
};

export default async function Home() {
  return <SaaSLanding />;
}
