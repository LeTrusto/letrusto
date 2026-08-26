import Link from "next/link";
import BrandMark from "./BrandMark";

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
  { label: "Contact", href: "/contact" },
  { label: "Support", href: "/support" },
];

const POLICY_LINKS = [
  { label: "Shipping Policy", href: "/shipping-policy" },
  { label: "Returns & Refunds", href: "/returns-policy" },
  { label: "Privacy Policy", href: "/privacy-policy" },
  { label: "Terms of Use", href: "/terms-of-use" },
];

export default function CommerceFooter() {
  return (
    <footer className="bg-[var(--lt-primary)] pb-24 text-white lg:pb-0">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 md:py-12">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div>
            <BrandMark footer />
            <p className="mt-3 text-sm text-zinc-400 leading-relaxed">
              Original designs, printed fresh.<br />
              Made to order and shipped worldwide.
            </p>
          </div>

          {/* Shop */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-4">Shop</h3>
            <ul className="space-y-2.5">
              {SHOP_LINKS.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-zinc-300 hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-4">Company</h3>
            <ul className="space-y-2.5">
              {COMPANY_LINKS.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-zinc-300 hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Policies */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-4">Policies</h3>
            <ul className="space-y-2.5">
              {POLICY_LINKS.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-zinc-300 hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-start justify-between gap-4 border-t border-zinc-800 pt-8 sm:flex-row sm:items-center">
          <p className="text-xs text-zinc-500">© {new Date().getFullYear()} LeTrusto. All rights reserved.</p>
          <div className="flex items-center gap-5">
            <a href="https://instagram.com/letrusto" target="_blank" rel="noopener noreferrer" className="text-zinc-500 hover:text-white transition-colors text-xs">
              Instagram
            </a>
            <a href="https://x.com/letrusto" target="_blank" rel="noopener noreferrer" className="text-zinc-500 hover:text-white transition-colors text-xs">
              X / Twitter
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
