"use client";

import Link from "next/link";
import BrandMark from "./BrandMark";
import { openCookiePreferences } from "@/components/CookieConsent";

export const footerLinks = {
  product: [
  { label: "Features", href: "/#features" },
  { label: "Pricing", href: "/#pricing" },
  { label: "Live Demo", href: "/demo" },
  { label: "About", href: "/about" },
  { label: "Dashboard", href: "/dashboard" },
  ],
  legal: [
  { label: "Privacy Policy", href: "/privacy" },
  { label: "Terms of Service", href: "/terms" },
  { label: "Contact Support", href: "/support" },
  { label: "Cookie Preferences", href: "#cookies", onClick: "openCookieModal" },
  ],
} as const;

const liveDemoScrollTarget = "/#demo";
export const legacyPolicyRedirects = ["/privacy-policy", "/terms-of-use"];

export default function CommerceFooter() {
  return (
    <footer className="relative z-10 pointer-events-auto border-t border-slate-800 bg-slate-950 pb-24 text-slate-300 lg:pb-0">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 md:py-12">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <BrandMark footer tone="light" />
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-slate-400">Social Proof, Made Visible.</p>
            <p className="mt-6 text-xs text-slate-500">© 2026 LeTrusto. All rights reserved.</p>
          </div>
          <div>
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Product</h3>
            <ul className="space-y-2.5">
              {footerLinks.product.map((link) => <li key={link.href}><Link href={link.href} data-scroll-target={link.label === "Live Demo" ? liveDemoScrollTarget : undefined} className="relative z-10 inline-block cursor-pointer pointer-events-auto text-sm text-slate-400 transition-colors duration-200 hover:text-amber-400">{link.label}</Link></li>)}
            </ul>
          </div>
          <div>
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Legal & Support</h3>
            <ul className="space-y-2.5">
              {footerLinks.legal.slice(0, 3).map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="relative z-10 inline-block cursor-pointer pointer-events-auto text-sm text-slate-400 transition-colors duration-200 hover:text-amber-400">
                    {link.label}
                  </Link>
                </li>
              ))}
              <li><a href="#cookies" onClick={(event) => { event.preventDefault(); openCookiePreferences(); }} className="relative z-10 inline-block cursor-pointer pointer-events-auto text-sm text-slate-400 transition-colors duration-200 hover:text-amber-400">Cookie Preferences</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-start justify-between gap-4 border-t border-slate-800 pt-8 sm:flex-row sm:items-center">
          <div className="flex items-center gap-5">
            <a href="https://instagram.com/letrusto" target="_blank" rel="noopener noreferrer" className="text-xs text-slate-500 transition-colors hover:text-white">
              Instagram
            </a>
            <a href="https://x.com/letrusto" target="_blank" rel="noopener noreferrer" className="text-xs text-slate-500 transition-colors hover:text-white">
              X / Twitter
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
