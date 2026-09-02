"use client";

import { useEffect, useRef } from "react";
import { trackSafeEvent, type SafeAnalyticsEvent, type SafeAnalyticsParams } from "@/lib/analytics";
import { useConsent } from "@/lib/consentContext";

export default function AnalyticsEvent({ event, params }: { event: SafeAnalyticsEvent; params?: SafeAnalyticsParams }) {
  const consent = useConsent();
  const tracked = useRef(false);

  useEffect(() => {
    if (tracked.current || !consent?.analytics) return;
    trackSafeEvent(event, params);
    tracked.current = true;
  }, [consent?.analytics, event, params]);

  return null;
}