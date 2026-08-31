"use client";

import Link from "next/link";
import BrandMark from "./BrandMark";
import { openCookiePreferences } from "@/components/CookieConsent";

const SHOP_LINKS = [
  { label: "All Products", href: "/shop" },
  { label: "Apparel", href: "/shop?category=apparel" },
  { label: "Wall Art", href: "/shop?category=wall-art" },
  { label: "Accessories", href: "/shop?category=accessories" },
  { label: "Home & Living", href: "/shop?category=home-living" },
  { label: "Stationery", href: "/shop?category=stationery" },
];

const COMPANY_LINKS = [
  { label: "About", href: "/about" },
  { label: "Contact Us", href: "/support?tab=contact&category=contact" },
  { label: "Support", href: "/support" },
];

const POLICY_LINKS = [
  { label: "Shipping Policy", href: "/shipping-policy" },
  { label: "Returns & Refunds", href: "/returns-policy" },
  { label: "Cancellation Policy", href: "/cancellation-policy" },
  { label: "Privacy Policy", href: "/privacy-policy" },
  { label: "Terms & Conditions", href: "/terms-of-use" },
];

export default function CommerceFooter() {
  return (
    <footer className="bg-[var(--background)] pb-24 text-[var(--text-primary)] lg:pb-0">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 md:py-12">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div>
            <BrandMark footer />
            <p className="mt-3 text-sm leading-relaxed text-[var(--text-secondary)]">
              Original designs, printed fresh.<br />
              Made to order for the current India launch.
            </p>
          </div>

          {/* Shop */}
          <div>
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">Shop</h3>
            <ul className="space-y-2.5">
              {SHOP_LINKS.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--lt-accent)]">
                    {link.label}
                  </Link>
                </li>
              ))}
              <li><button type="button" onClick={openCookiePreferences} className="text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--lt-accent)]">Cookie Preferences</button></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">Company</h3>
            <ul className="space-y-2.5">
              {COMPANY_LINKS.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--lt-accent)]">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Policies */}
          <div>
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">Policies</h3>
            <ul className="space-y-2.5">
              {POLICY_LINKS.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--lt-accent)]">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-start justify-between gap-4 border-t border-[var(--border)] pt-8 sm:flex-row sm:items-center">
          <p className="text-xs text-[var(--text-muted)]">© {new Date().getFullYear()} LeTrusto. All rights reserved.</p>
          <div className="flex items-center gap-5">
            <a href="https://instagram.com/letrusto" target="_blank" rel="noopener noreferrer" className="text-xs text-[var(--text-muted)] transition-colors hover:text-[var(--lt-accent)]">
              Instagram
            </a>
            <a href="https://x.com/letrusto" target="_blank" rel="noopener noreferrer" className="text-xs text-[var(--text-muted)] transition-colors hover:text-[var(--lt-accent)]">
              X / Twitter
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
