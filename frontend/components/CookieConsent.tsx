"use client";

import { useEffect, useState, useSyncExternalStore } from "react";

import { getConsent, saveConsent, subscribeToConsent } from "@/lib/consent";

const OPEN_PREFERENCES_EVENT = "letrusto:open-cookie-preferences";

export function openCookiePreferences(): void {
  window.dispatchEvent(new Event(OPEN_PREFERENCES_EVENT));
}

export default function CookieConsent() {
  const consent = useSyncExternalStore(subscribeToConsent, getConsent, () => null);
  const [preferencesOpen, setPreferencesOpen] = useState(false);
  const [analytics, setAnalytics] = useState(false);
  const [marketing, setMarketing] = useState(false);

  useEffect(() => {
    const open = () => {
      const current = getConsent();
      setAnalytics(current?.analytics ?? false);
      setMarketing(current?.marketing ?? false);
      setPreferencesOpen(true);
    };
    window.addEventListener(OPEN_PREFERENCES_EVENT, open);
    return () => window.removeEventListener(OPEN_PREFERENCES_EVENT, open);
  }, []);

  function choose(nextAnalytics: boolean, nextMarketing: boolean) {
    saveConsent(nextAnalytics, nextMarketing);
    setPreferencesOpen(false);
  }

  function manage() {
    setAnalytics(consent?.analytics ?? false);
    setMarketing(consent?.marketing ?? false);
    setPreferencesOpen(true);
  }

  return (
    <>
      {!consent && !preferencesOpen && (
        <aside role="dialog" aria-label="Cookie consent" className="fixed inset-x-3 bottom-3 z-[70] rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface)] p-4 shadow-[var(--shadow-premium)] sm:inset-x-auto sm:right-6 sm:bottom-6 sm:max-w-xl sm:p-5">
          <h2 className="text-base font-bold text-[var(--text-primary)]">Cookie preferences</h2>
          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">We use essential cookies to keep LeTrusto working. With your permission, we may also use optional cookies for analytics and marketing.</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <button type="button" onClick={() => choose(true, true)} className="lt-btn lt-btn-primary">Accept All</button>
            <button type="button" onClick={() => choose(false, false)} className="lt-btn lt-btn-secondary">Reject Non-Essential</button>
            <button type="button" onClick={manage} className="lt-btn lt-btn-secondary">Manage Preferences</button>
          </div>
        </aside>
      )}
      {preferencesOpen && (
        <div role="presentation" className="fixed inset-0 z-[80] flex items-end justify-center bg-slate-950/30 p-3 sm:items-center">
          <section role="dialog" aria-modal="true" aria-labelledby="cookie-preferences-title" className="w-full max-w-lg rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[var(--shadow-premium)] sm:p-6">
            <h2 id="cookie-preferences-title" className="text-xl font-bold text-[var(--text-primary)]">Cookie preferences</h2>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">Choose which optional technologies may help us understand and improve the storefront. Essential storage is always active because it is required for security, your cart, checkout, payments, and sign-in.</p>
            <PreferenceRow label="Essential" description="Always Active" checked disabled />
            <PreferenceRow label="Analytics" description="Helps us understand storefront performance." checked={analytics} onChange={setAnalytics} />
            <PreferenceRow label="Marketing" description="No marketing tools are currently configured." checked={marketing} onChange={setMarketing} />
            <div className="mt-6 flex justify-end">
              <button type="button" onClick={() => choose(analytics, marketing)} className="lt-btn lt-btn-primary">Save Preferences</button>
            </div>
          </section>
        </div>
      )}
    </>
  );
}

function PreferenceRow({ label, description, checked, disabled, onChange }: { label: string; description: string; checked: boolean; disabled?: boolean; onChange?: (value: boolean) => void }) {
  return <label className="mt-4 flex items-center justify-between gap-4 border-t border-[var(--border)] pt-4"><span><span className="block text-sm font-semibold text-[var(--text-primary)]">{label}</span><span className="block text-xs text-[var(--text-secondary)]">{description}</span></span><input type="checkbox" checked={checked} disabled={disabled} onChange={(event) => onChange?.(event.target.checked)} className="h-5 w-5 accent-[var(--lt-purple)]" aria-label={`${label} cookies`} /></label>;
}
