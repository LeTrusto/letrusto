import type { Metadata } from "next";

import SchemaOrg from "@/components/SchemaOrg";
import AboutExperience from "@/components/saas/AboutExperience";

export const metadata: Metadata = {
  title: "About LeTrusto",
  description: "Learn how LeTrusto helps growing businesses turn customer confidence into visible momentum.",
  alternates: {
    canonical: "/about",
  },
  openGraph: {
    title: "About LeTrusto",
    description: "Learn how LeTrusto helps growing businesses turn customer confidence into visible momentum.",
    url: "/about",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "About LeTrusto",
    description: "Learn how LeTrusto helps growing businesses turn customer confidence into visible momentum.",
    images: ["/images/og-default.svg"],
  },
};

export default function AboutPage() {
  return (
    <>
      <SchemaOrg
        type="WebPage"
        data={{
          name: "About LeTrusto",
          url: "https://letrusto.com/about",
          description: "Learn how LeTrusto helps growing businesses turn customer confidence into visible momentum.",
        }}
      />
      <AboutExperience />
    </>
  );
}
