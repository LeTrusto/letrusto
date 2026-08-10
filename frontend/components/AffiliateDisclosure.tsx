"use client";

import { X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const STORAGE_KEY = "lt_aff_disclosure_v1";

/**
 * Slim site-wide affiliate disclosure banner.
 * Renders once per browser session; dismissed state persists in localStorage.
 * Place between <Navbar /> and {children} in the root layout.
 */
export default function AffiliateDisclosure() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    try {
      if (!localStorage.getItem(STORAGE_KEY)) {
        setVisible(true);
      }
    } catch {
      // localStorage unavailable (private mode, etc.) — show the banner
      setVisible(true);
    }
  }, []);

  function dismiss() {
    try {
      localStorage.setItem(STORAGE_KEY, "1");
    } catch {
      // ignore
    }
    setVisible(false);
  }

  if (!visible) return null;

  return (
    <div
      role="note"
      aria-label="Affiliate disclosure"
      className="border-b border-slate-200 bg-slate-50 px-4 py-2"
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3">
        <p className="text-xs leading-relaxed text-slate-600">
          <strong className="font-semibold text-slate-800">Affiliate disclosure:</strong>{" "}
          LeTrusto may earn a commission when you purchase through qualifying
          links. This does not change the price you pay, and we only recommend
          products we believe are relevant to our users.{" "}
          <Link
            href="/affiliate-disclosure"
            className="font-medium text-purple-700 underline underline-offset-2 hover:text-purple-900"
          >
            Learn more
          </Link>
        </p>
        <button
          onClick={dismiss}
          aria-label="Dismiss affiliate disclosure"
          className="flex-shrink-0 rounded p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
        >
          <X size={13} aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
