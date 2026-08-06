import type { Metadata } from "next";

import HomepageSectionRenderer from "@/components/homepage/HomepageSectionRenderer";
import { HOMEPAGE_SECTIONS } from "@/config/homepage";
import { getHomepageDataSources } from "@/services/homepage.service";

export const metadata: Metadata = {
  title: "Know Before You Buy",
  description:
    "LeTrusto is your AI Buying Advisor. Compare electronics, get personalized recommendations, and buy with confidence.",
  alternates: {
    canonical: "/",
  },
};

export default async function Home() {
  const dataSources = await getHomepageDataSources();
  const sections = HOMEPAGE_SECTIONS.filter((section) => section.enabled).sort(
    (left, right) => left.order - right.order
  );

  return (
    <main>
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
