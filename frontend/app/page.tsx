import type { Metadata } from "next";

import HomepageSectionRenderer from "@/components/homepage/HomepageSectionRenderer";
import SchemaOrg from "@/components/SchemaOrg";
import { HOMEPAGE_SECTIONS } from "@/config/homepage";
import { getHomepageDataSources } from "@/services/homepage.service";

export const metadata: Metadata = {
  title: "AI Tools and Software Buying Advisor",
  description:
    "LeTrusto helps teams compare AI tools, discover trusted software recommendations, and choose confidently before they pay.",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "LeTrusto",
    description: "AI-powered buying advisor for AI tools and software.",
    url: "/",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "LeTrusto",
    description: "AI-powered buying advisor for AI tools and software.",
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
          description: "LeTrusto helps teams compare AI tools, discover trusted software recommendations, and choose confidently before they pay.",
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
