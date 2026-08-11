import Link from "next/link";

const FOOTER_LINKS = {
  Product: [
    { label: "Ask LeTrusto", href: "/ai" },
    { label: "AI Tools", href: "/ai-tools" },
    { label: "Buying Guides", href: "/guides" },
    { label: "Search", href: "/search" },
    { label: "Compare", href: "/compare" },
    { label: "Favourites", href: "/favorites" },
  ],
  Categories: [
    { label: "AI Assistants", href: "/category/ai-assistants" },
    { label: "AI Writing", href: "/category/ai-writing" },
    { label: "AI Image & Design", href: "/category/ai-image-design" },
    { label: "AI Video & Audio", href: "/category/ai-video-audio" },
    { label: "AI Coding & Developer Tools", href: "/category/ai-coding-developer-tools" },
    { label: "Marketing & Automation", href: "/category/marketing-automation" },
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
            <Link href="/" className="inline-flex items-center gap-2">
              <span className="text-[1.625rem] font-black tracking-tight">
                <span className="bg-gradient-to-r from-[var(--lt-purple)] to-[var(--lt-pink)] bg-clip-text text-transparent">Le</span>
                <span className="text-slate-900">Trusto</span>
              </span>
            </Link>
            <p className="mt-4 text-sm leading-relaxed text-[var(--text-secondary)]">
              Research-backed AI tool and software recommendations, comparisons, and buying guidance for teams that want clarity before they pay.
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

        {/* Affiliate disclosure */}
        <div className="mt-12 rounded-[var(--radius-lg)] bg-[var(--surface-muted)] px-5 py-4 text-xs leading-relaxed text-[var(--text-muted)]">
          <strong className="font-semibold text-[var(--text-secondary)]">Affiliate Disclosure:</strong>{" "}
          LeTrusto may earn a commission when you click affiliate links and make a purchase. This does not change the price you pay. We only recommend products we genuinely evaluate.{" "}
          <Link href="/affiliate-disclosure" className="underline transition hover:text-[var(--lt-purple)]">
            Full disclosure
          </Link>
        </div>

        {/* Bottom bar */}
        <div className="mt-8 flex flex-col items-center justify-between gap-3 border-t border-[var(--border)] pt-8 sm:flex-row">
          <p className="text-xs text-[var(--text-muted)]">
            © {new Date().getFullYear()} LeTrusto. All rights reserved.
          </p>
          <p className="text-xs text-[var(--text-muted)]">
            Built for clearer, more confident buying decisions
          </p>
        </div>
      </div>
    </footer>
  );
}
