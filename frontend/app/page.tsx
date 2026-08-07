import type { Metadata } from "next";

import HomepageSectionRenderer from "@/components/homepage/HomepageSectionRenderer";
import SchemaOrg from "@/components/SchemaOrg";
import { HOMEPAGE_SECTIONS } from "@/config/homepage";
import { getHomepageDataSources } from "@/services/homepage.service";

export const metadata: Metadata = {
  title: "AI Buying Advisor",
  description:
    "LeTrusto helps people compare products, discover trusted recommendations, and buy with confidence.",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "LeTrusto",
    description: "Compare products, get AI recommendations, and shop with confidence.",
    url: "/",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "LeTrusto",
    description: "Compare products, get AI recommendations, and shop with confidence.",
    images: ["/images/og-default.svg"],
  },
};

export default async function Home() {
  const dataSources = await getHomepageDataSources();
  const sections = HOMEPAGE_SECTIONS.filter((section) => section.enabled).sort(
    (left, right) => left.order - right.order
  );

  return (
    <main>
      <SchemaOrg
        type="WebPage"
        data={{
          name: "LeTrusto",
          url: "https://letrusto.com",
          description: "LeTrusto helps people compare products, discover trusted recommendations, and buy with confidence.",
        }}
      />
      {sections.map((section) => (
        <HomepageSectionRenderer
          key={section.id}
          section={section}
          dataSources={dataSources}
        />
      ))}
    </main>
  );
}
