import Hero from "@/components/Hero";
import HomeCategoryShowcase from "@/components/homepage/HomeCategoryShowcase";
import HomeTrustSignalsSection from "@/components/homepage/HomeTrustSignalsSection";
import HomeLatestGuidesSection from "@/components/homepage/HomeLatestGuidesSection";
import HomeAskAiCtaSection from "@/components/homepage/HomeAskAiCtaSection";
import HomePopularComparisonsSection from "@/components/homepage/HomePopularComparisonsSection";
import HomeComingSoonVerticalSection from "@/components/homepage/HomeComingSoonVerticalSection";
import type { HomepageSectionConfig } from "@/config/homepage";
import type { HomepageDataSources } from "@/services/homepage.service";

type HomepageSectionRendererProps = {
  section: HomepageSectionConfig;
  dataSources: HomepageDataSources;
};

function resolveItems<K extends keyof HomepageDataSources>(
  dataSources: HomepageDataSources,
  key: K,
  maxItems?: number
): HomepageDataSources[K] {
  const items = dataSources[key];
  if (!Array.isArray(items) || maxItems === undefined) {
    return items;
  }

  return items.slice(0, maxItems) as HomepageDataSources[K];
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

    case "trustSignals": {
      const items = resolveItems(dataSources, "trust.default", section.maxItems);
      return (
        <HomeTrustSignalsSection
          title={section.title ?? "Why Trust LeTrusto"}
          subtitle={section.subtitle}
          items={items}
        />
      );
    }

    case "comparisons": {
      const items = resolveItems(dataSources, "comparisons.popular", section.maxItems);
      return (
        <HomePopularComparisonsSection
          title={section.title ?? "Popular Comparisons"}
          subtitle={section.subtitle}
          ctaLabel={section.ctaLabel}
          ctaHref={section.ctaHref}
          items={items}
        />
      );
    }

    case "comingSoonVertical": {
      const source = section.dataSource;
      const item =
        source === "comingSoon.hostingSaas"
          ? dataSources["comingSoon.hostingSaas"]
          : source === "comingSoon.beauty"
            ? dataSources["comingSoon.beauty"]
            : source === "comingSoon.petCare"
              ? dataSources["comingSoon.petCare"]
              : null;

      if (!item) {
        return null;
      }

      return (
        <HomeComingSoonVerticalSection
          title={section.title ?? item.title}
          item={item}
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
