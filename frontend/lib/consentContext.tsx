"use client";

import { createContext, useContext, useSyncExternalStore } from "react";

import { getConsent, subscribeToConsent, type ConsentState } from "@/lib/consent";

const ConsentContext = createContext<ConsentState | null>(null);

export function ConsentProvider({ children }: { children: React.ReactNode }) {
  const consent = useSyncExternalStore(subscribeToConsent, getConsent, () => null);
  return <ConsentContext.Provider value={consent}>{children}</ConsentContext.Provider>;
}

export function useConsent(): ConsentState | null {
  return useContext(ConsentContext);
}