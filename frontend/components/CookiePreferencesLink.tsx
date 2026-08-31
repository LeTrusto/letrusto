"use client";

import { openCookiePreferences } from "@/components/CookieConsent";

export default function CookiePreferencesLink() {
  return <button type="button" onClick={openCookiePreferences} className="mt-2 underline">Manage Cookie Preferences</button>;
}