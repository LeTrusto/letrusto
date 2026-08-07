import type { Metadata } from "next";
import SchemaOrg from "@/components/SchemaOrg";
import SupportPage from "./SupportPage";

export const metadata: Metadata = {
  title: "Support Centre",
  description: "Get help with LeTrusto — FAQ, contact us, report issues, and submit feedback.",
  alternates: {
    canonical: "/support",
  },
  openGraph: {
    title: "Support Centre",
    description: "Get help with LeTrusto — FAQ, contact us, report issues, and submit feedback.",
    url: "/support",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Support Centre",
    description: "Get help with LeTrusto — FAQ, contact us, report issues, and submit feedback.",
    images: ["/images/og-default.svg"],
  },
};

export default function SupportPageRoute() {
  return (
    <>
      <SchemaOrg
        type="WebPage"
        data={{
          name: "Support Centre",
          url: "https://letrusto.com/support",
          description: "Get help with LeTrusto — FAQ, contact us, report issues, and submit feedback.",
        }}
      />
      <SupportPage />
    </>
  );
}
