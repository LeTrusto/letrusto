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
    <footer className="mt-auto border-t border-gray-100 bg-white">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4 lg:gap-12">
          {/* Brand column */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="inline-flex items-center gap-2">
              <span className="text-2xl font-black">
                <span className="text-pink-600">Le</span>
                <span className="text-gray-900">Trusto</span>
              </span>
            </Link>
            <p className="mt-3 text-sm leading-relaxed text-gray-500">
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
                  className="flex h-9 w-9 items-center justify-center rounded-xl border border-gray-200 text-sm text-gray-500 transition hover:border-purple-300 hover:text-purple-600"
                >
                  {s.icon}
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(FOOTER_LINKS).map(([heading, links]) => (
            <div key={heading}>
              <h3 className="mb-4 text-sm font-bold uppercase tracking-widest text-gray-900">{heading}</h3>
              <ul className="space-y-2.5">
                {links.map(({ label, href }) => (
                  <li key={label}>
                    <Link
                      href={href}
                      className="text-sm text-gray-500 transition hover:text-purple-700"
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
        <div className="mt-10 rounded-xl bg-gray-50 px-5 py-4 text-xs text-gray-400">
          <strong className="font-semibold text-gray-500">Affiliate Disclosure:</strong>{" "}
          LeTrusto may earn a commission when you click affiliate links and make a purchase. This does not change the price you pay. We only recommend products we genuinely evaluate.{" "}
          <Link href="/affiliate-disclosure" className="underline hover:text-gray-600">
            Full disclosure
          </Link>
        </div>

        {/* Bottom bar */}
        <div className="mt-6 flex flex-col items-center justify-between gap-3 border-t border-gray-100 pt-6 sm:flex-row">
          <p className="text-xs text-gray-400">
            © {new Date().getFullYear()} LeTrusto. All rights reserved.
          </p>
          <p className="text-xs text-gray-400">
            Built for clearer, more confident buying decisions
          </p>
        </div>
      </div>
    </footer>
  );
}
