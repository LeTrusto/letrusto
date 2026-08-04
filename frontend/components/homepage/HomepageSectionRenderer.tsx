import Hero from "@/components/Hero";
import HomeCategoryShowcase from "@/components/homepage/HomeCategoryShowcase";
import HomeProductGridSection from "@/components/homepage/HomeProductGridSection";
import HomeProductRailSection from "@/components/homepage/HomeProductRailSection";
import HomeAIPicksFeaturedSection from "@/components/homepage/HomeAIPicksFeaturedSection";
import HomeDealsSpotlightSection from "@/components/homepage/HomeDealsSpotlightSection";
import HomeComingSoonRoadmapSection from "@/components/homepage/HomeComingSoonRoadmapSection";
import HomeTrustSignalsSection from "@/components/homepage/HomeTrustSignalsSection";
import HomeLatestGuidesSection from "@/components/homepage/HomeLatestGuidesSection";
import HomeAskAiCtaSection from "@/components/homepage/HomeAskAiCtaSection";
import type { HomepageSectionConfig } from "@/config/homepage";
import type { HomepageDataSources } from "@/services/homepage.service";

type ProductSourceKey =
  | "products.trending"
  | "products.newArrivals"
  | "products.aiPicks"
  | "products.bestDeals";

const PRODUCT_SOURCE_KEYS: ProductSourceKey[] = [
  "products.trending",
  "products.newArrivals",
  "products.aiPicks",
  "products.bestDeals",
];

function isProductSourceKey(value: string): value is ProductSourceKey {
  return PRODUCT_SOURCE_KEYS.includes(value as ProductSourceKey);
}

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

    case "productGrid": {
      if (!isProductSourceKey(section.dataSource)) {
        return null;
      }

      const items = resolveItems(dataSources, section.dataSource, section.maxItems);

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
      if (!isProductSourceKey(section.dataSource)) {
        return null;
      }

      const items = resolveItems(dataSources, section.dataSource, section.maxItems);

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

    case "aiFeatured": {
      const items = resolveItems(dataSources, "products.aiPicks", section.maxItems);
      return (
        <HomeAIPicksFeaturedSection
          title={section.title ?? "AI Picks"}
          subtitle={section.subtitle}
          ctaLabel={section.ctaLabel}
          ctaHref={section.ctaHref}
          items={items}
        />
      );
    }

    case "dealsSpotlight": {
      const items = resolveItems(dataSources, "products.bestDeals", section.maxItems);
      return (
        <HomeDealsSpotlightSection
          title={section.title ?? "Best Deals"}
          subtitle={section.subtitle}
          ctaLabel={section.ctaLabel}
          ctaHref={section.ctaHref}
          items={items}
        />
      );
    }

    case "comingSoonRoadmap": {
      const items = resolveItems(dataSources, "comingSoon.verticals", section.maxItems);
      return (
        <HomeComingSoonRoadmapSection
          title={section.title ?? "Coming Soon"}
          subtitle={section.subtitle}
          ctaLabel={section.ctaLabel}
          ctaHref={section.ctaHref}
          items={items}
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
