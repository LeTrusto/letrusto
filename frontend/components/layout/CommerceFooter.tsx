import Link from "next/link";

const SHOP_LINKS = [
  { label: "All Products", href: "/shop" },
  { label: "Jewellery", href: "/shop?category=jewellery" },
  { label: "Hair & Style", href: "/shop?category=hair-style" },
  { label: "Beauty Tools", href: "/shop?category=beauty-tools" },
  { label: "Accessories", href: "/shop?category=accessories" },
  { label: "Gifts", href: "/shop?category=gifts" },
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
    <footer className="hidden md:block bg-[var(--lt-primary)] text-white">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <Link href="/" className="text-xl font-extrabold tracking-tight">
              LeTrusto
            </Link>
            <p className="mt-3 text-sm text-zinc-400 leading-relaxed">
              Trending finds. Everyday prices.<br />
              Curated beauty, jewellery &amp; style.
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

        <div className="mt-10 pt-8 border-t border-zinc-800 flex flex-col sm:flex-row items-center justify-between gap-4">
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
