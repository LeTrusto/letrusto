"use client";

import { useEffect, useMemo, useRef } from "react";
import { usePathname } from "next/navigation";
import { trackSafeEvent, type SafeAnalyticsEvent, type SafeAnalyticsParams } from "@/lib/analytics";
import { getDigitalProductBySlug } from "@/lib/digitalProducts";
import { getServiceBySlug } from "@/lib/services";
import { useConsent } from "@/lib/consentContext";

const TOOL_NAMES = new Set(["profit-margin-calculator", "invoice-generator", "pricing-calculator", "break-even-calculator", "expense-calculator", "commission-calculator", "discount-calculator", "freelancer-rate-calculator"]);

export default function FunnelAnalytics() {
  const pathname = usePathname();
  const consent = useConsent();
  const trackedRoute = useRef<string | null>(null);
  const routeEvent = useMemo<{ event: SafeAnalyticsEvent; params: SafeAnalyticsParams } | null>(() => {
    const segments = pathname.split("/").filter(Boolean);
    if (segments[0] === "tools" && TOOL_NAMES.has(segments[1] ?? "")) return { event: "tool_view" as const, params: { tool_name: segments[1] ?? "" } as SafeAnalyticsParams };
    if (pathname === "/digital-products") return { event: "digital_products_view" as const, params: { page: "digital-products" } as SafeAnalyticsParams };
    if (segments[0] === "digital-products" && segments[1]) {
      const product = getDigitalProductBySlug(segments[1]);
      if (product) return { event: "digital_product_view" as const, params: { product_name: product.name, product_slug: product.slug } as SafeAnalyticsParams };
    }
    if (pathname === "/services") return { event: "services_view" as const, params: { page: "services" } as SafeAnalyticsParams };
    if (segments[0] === "services" && segments[1] && segments[1] !== "quote") {
      const service = getServiceBySlug(segments[1]);
      if (service) return { event: "service_detail_view" as const, params: { service_name: service.name, service_slug: service.slug } as SafeAnalyticsParams };
    }
    return null;
  }, [pathname]);

  useEffect(() => {
    if (!routeEvent || !consent?.analytics || trackedRoute.current === pathname) return;
    trackSafeEvent(routeEvent.event, routeEvent.params);
    trackedRoute.current = pathname;
  }, [consent?.analytics, pathname, routeEvent]);

  return null;
}