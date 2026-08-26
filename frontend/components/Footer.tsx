import Image from "next/image";
import Link from "next/link";

const FOOTER_LINKS = {
  Product: [
    { label: "Shop all designs", href: "/shop" },
    { label: "How it works", href: "/how-it-works" },
    { label: "Search products", href: "/shop" },
    { label: "Cart", href: "/cart" },
    { label: "Favourites", href: "/favorites" },
  ],
  Categories: [
    { label: "Apparel", href: "/shop?category=apparel" },
    { label: "Wall Art", href: "/shop?category=wall-art" },
    { label: "Accessories", href: "/shop?category=accessories" },
    { label: "Home & Living", href: "/shop?category=home-living" },
    { label: "Stationery", href: "/shop?category=stationery" },
  ],
  Company: [
    { label: "About", href: "/about" },
    { label: "Research Methodology", href: "/methodology" },
    { label: "Affiliate Disclosure", href: "/affiliate-disclosure" },
    { label: "Support", href: "/support" },
    { label: "Contact Us", href: "/contact" },
    { label: "Privacy Policy", href: "/privacy-policy" },
    { label: "Terms of Use", href: "/terms-of-use" },
    { label: "Report Issue", href: "/report-issue" },
  ],
};

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-[var(--border)] bg-white">
      <div className="mx-auto max-w-7xl px-6 py-14">
        <div className="grid grid-cols-2 gap-10 md:grid-cols-4 lg:gap-14">
          {/* Brand column */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" aria-label="LeTrusto home" className="inline-flex items-center">
              <Image src="/LeTrusto%20Brand%20Logo.png" alt="LeTrusto - Discover. Choose. Trust." width={1774} height={887} priority unoptimized className="h-auto w-40" />
            </Link>
            <p className="mt-4 text-sm leading-relaxed text-[var(--text-secondary)]">
              Original designs printed fresh on products you can wear, carry, and live with. Made to order and shipped worldwide.
            </p>
            <div className="mt-5 flex gap-3">
              {[
                { label: "Twitter / X", href: "https://x.com/letrusto", icon: "𝕏" },
                { label: "Instagram", href: "https://instagram.com/letrusto", icon: "📷" },
              ].map((s) => (
                <a
                  key={s.label}
                  href={s.href}
                  aria-label={s.label}
                  target="_blank"
                  rel="me noopener noreferrer"
                  className="flex h-10 w-10 items-center justify-center rounded-[var(--radius-lg)] border border-[var(--border)] text-sm text-[var(--text-muted)] transition hover:border-[var(--lt-purple-light)] hover:text-[var(--lt-purple)]"
                >
                  {s.icon}
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(FOOTER_LINKS).map(([heading, links]) => (
            <div key={heading}>
              <h3 className="lt-label mb-4">{heading}</h3>
              <ul className="space-y-3">
                {links.map(({ label, href }) => (
                  <li key={label}>
                    <Link
                      href={href}
                      className="text-sm text-[var(--text-secondary)] transition hover:text-[var(--lt-purple)]"
                    >
                      {label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Store disclosure */}
        <div className="mt-12 rounded-[var(--radius-lg)] bg-[var(--surface-muted)] px-5 py-4 text-xs leading-relaxed text-[var(--text-muted)]">
          <strong className="font-semibold text-[var(--text-secondary)]">Made to order:</strong>{" "}
          Each product is created after you order, helping us avoid unnecessary inventory while keeping every design intentional.{" "}
          <Link href="/how-it-works" className="underline transition hover:text-[var(--lt-purple)]">
            Learn how it works
          </Link>
        </div>

        {/* Bottom bar */}
        <div className="mt-8 flex flex-col items-center justify-between gap-3 border-t border-[var(--border)] pt-8 sm:flex-row">
          <p className="text-xs text-[var(--text-muted)]">
            © {new Date().getFullYear()} LeTrusto. All rights reserved.
          </p>
          <p className="text-xs text-[var(--text-muted)]">
            Designed for more personal everyday goods
          </p>
        </div>
      </div>
    </footer>
  );
}
