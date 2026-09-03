import type { Metadata } from "next";

import Hero from "@/components/home/Hero";
import NewsletterSignup from "@/components/home/NewsletterSignup";
import SchemaOrg from "@/components/SchemaOrg";
import { SITE_URL } from "@/config/site";

export const metadata: Metadata = {
  title: "Tools, Templates & Digital Services",
  description: "Practical free tools, ready-to-use digital products and affordable digital services for Indian businesses, freelancers and creators.",
  alternates: { canonical: "/" },
  openGraph: {
    title: "LeTrusto — Tools, Templates & Digital Services",
    description: "Practical free tools, ready-to-use digital products and affordable digital services for Indian businesses, freelancers and creators.",
    url: "/",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
};

export default async function Home() {
  return (
    <main className="bg-[var(--background)]">
      <SchemaOrg type="WebPage" data={{ name: "LeTrusto — Digital tools and services", url: SITE_URL, description: "Practical digital tools, templates and services for Indian businesses." }} />
      <Hero />
      <NewsletterSignup />
    </main>
  );
}
