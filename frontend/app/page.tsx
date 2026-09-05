import type { Metadata } from "next";

import SaaSLanding from "@/components/saas/SaasLanding";

export const metadata: Metadata = {
  title: { absolute: "LeTrusto - Social Proof Widgets for Growing Businesses" },
  description: "LeTrusto helps growing businesses collect, manage, and display customer reviews and social proof with lightweight widgets.",
  alternates: { canonical: "/" },
  openGraph: {
    title: "LeTrusto",
    description: "LeTrusto helps growing businesses collect, manage, and display customer reviews and social proof with lightweight widgets.",
    url: "/",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/og-card.png", width: 1254, height: 1254 }],
  },
};

export default async function Home() {
  return <SaaSLanding />;
}
