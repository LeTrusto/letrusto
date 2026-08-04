import Hero from "@/components/Hero";
import HomeCategoryShowcase from "@/components/homepage/HomeCategoryShowcase";
import HomeProductGridSection from "@/components/homepage/HomeProductGridSection";
import HomeProductRailSection from "@/components/homepage/HomeProductRailSection";
import HomeTrustSignalsSection from "@/components/homepage/HomeTrustSignalsSection";
import HomeLatestGuidesSection from "@/components/homepage/HomeLatestGuidesSection";
import HomeAskAiCtaSection from "@/components/homepage/HomeAskAiCtaSection";
import type { HomepageSectionConfig } from "@/config/homepage";
import type { HomepageDataSources } from "@/services/homepage.service";

type HomepageSectionRendererProps = {
  section: HomepageSectionConfig;
  dataSources: HomepageDataSources;
};

function resolveItems(
  dataSources: HomepageDataSources,
  key: keyof HomepageDataSources,
  maxItems?: number
) {
  const items = dataSources[key];
  if (!Array.isArray(items) || maxItems === undefined) {
    return items;
  }

  return items.slice(0, maxItems);
}

export default function HomepageSectionRenderer({
  section,
  dataSources,
}: HomepageSectionRendererProps) {
  switch (section.component) {
    case "hero":
      return <Hero />;

    case "categoryShowcase": {
      const items = resolveItems(dataSources, "categories.showcase", section.maxItems);
      return (
        <HomeCategoryShowcase
          title={section.title ?? "Browse Categories"}
          subtitle={section.subtitle}
          items={items}
        />
      );
    }

    case "productGrid": {
      if (!section.dataSource.startsWith("products.")) {
        return null;
      }

      const items = resolveItems(
        dataSources,
        section.dataSource as keyof HomepageDataSources,
        section.maxItems
      );

      if (!Array.isArray(items)) {
        return null;
      }

      return (
        <HomeProductGridSection
          title={section.title ?? "Products"}
          subtitle={section.subtitle}
          ctaLabel={section.ctaLabel}
          ctaHref={section.ctaHref}
          items={items}
          highlightLabel={section.highlightLabel}
        />
      );
    }

    case "productRail": {
      if (!section.dataSource.startsWith("products.")) {
        return null;
      }

      const items = resolveItems(
        dataSources,
        section.dataSource as keyof HomepageDataSources,
        section.maxItems
      );

      if (!Array.isArray(items)) {
        return null;
      }

      return (
        <HomeProductRailSection
          title={section.title ?? "Products"}
          subtitle={section.subtitle}
          ctaLabel={section.ctaLabel}
          ctaHref={section.ctaHref}
          items={items}
          highlightLabel={section.highlightLabel}
        />
      );
    }

    case "trustSignals": {
      const items = resolveItems(dataSources, "trust.default", section.maxItems);
      return (
        <HomeTrustSignalsSection
          title={section.title ?? "Why Trust LeTrusto?"}
          subtitle={section.subtitle}
          items={items}
        />
      );
    }

    case "guides": {
      const items = resolveItems(dataSources, "guides.latest", section.maxItems);
      return (
        <HomeLatestGuidesSection
          title={section.title ?? "Latest Buying Guides"}
          subtitle={section.subtitle}
          ctaLabel={section.ctaLabel}
          ctaHref={section.ctaHref}
          items={items}
        />
      );
    }

    case "askAiCta":
      return (
        <HomeAskAiCtaSection
          title={section.title ?? "Ask LeTrusto AI"}
          subtitle={section.subtitle}
          ctaLabel={section.ctaLabel}
          ctaHref={section.ctaHref}
        />
      );

    default:
      return null;
  }
}
