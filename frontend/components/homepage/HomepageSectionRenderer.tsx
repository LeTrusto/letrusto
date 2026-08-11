import Hero from "@/components/Hero";
import HomeAskLetrustoSection from "@/components/homepage/HomeAskLetrustoSection";
import HomeCategoryShowcase from "@/components/homepage/HomeCategoryShowcase";
import HomeFeaturedToolsSection from "@/components/homepage/HomeFeaturedToolsSection";
import HomeTrustSignalsSection from "@/components/homepage/HomeTrustSignalsSection";
import HomeLatestGuidesSection from "@/components/homepage/HomeLatestGuidesSection";
import HomePopularComparisonsSection from "@/components/homepage/HomePopularComparisonsSection";
import HomeFeaturedBrandsSection from "@/components/homepage/HomeFeaturedBrandsSection";
import HomeNewsletterSection from "@/components/homepage/HomeNewsletterSection";
import HomeProductRailSection from "@/components/homepage/HomeProductRailSection";
import HomeTrendingSearchesSection from "@/components/homepage/HomeTrendingSearchesSection";
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

    case "featuredTools": {
      const tools = dataSources["tools.featured"];
      return (
        <HomeFeaturedToolsSection
          title={section.title ?? "Featured AI Tools"}
          subtitle={section.subtitle}
          tools={tools}
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

    case "productRail": {
      const dataKey = section.dataSource;
      const items =
        dataKey === "products.trending"
          ? resolveItems(dataSources, "products.trending", section.maxItems)
          : dataKey === "products.featured"
            ? resolveItems(dataSources, "products.featured", section.maxItems)
            : dataKey === "products.newArrivals"
              ? resolveItems(dataSources, "products.newArrivals", section.maxItems)
              : [];

      return (
        <HomeProductRailSection
          title={section.title ?? "Featured Products"}
          subtitle={section.subtitle}
          ctaLabel={section.ctaLabel}
          ctaHref={section.ctaHref}
          items={items}
          highlightLabel={section.highlightLabel}
        />
      );
    }

    case "featuredBrands": {
      const items = resolveItems(dataSources, "brands.featured", section.maxItems);
      return (
        <HomeFeaturedBrandsSection
          title={section.title ?? "Featured Brands"}
          subtitle={section.subtitle}
          items={items}
        />
      );
    }

    case "trendingSearches": {
      const items = resolveItems(dataSources, "searches.trending", section.maxItems);
      return (
        <HomeTrendingSearchesSection
          title={section.title ?? "Trending Searches"}
          subtitle={section.subtitle}
          items={items}
        />
      );
    }

    case "askLeTrusto":
      return <HomeAskLetrustoSection />;

    case "newsletter":
      return (
        <HomeNewsletterSection
          title={section.title ?? "Stay in the loop"}
          subtitle={section.subtitle}
          ctaLabel={section.ctaLabel}
          ctaHref={section.ctaHref}
        />
      );

    default:
      return null;
  }
}
