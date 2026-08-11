import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Affiliate Disclosure",
  description:
    "LeTrusto's affiliate disclosure policy. Learn how we handle affiliate relationships, commissions, and editorial independence.",
  alternates: {
    canonical: "/affiliate-disclosure",
  },
  openGraph: {
    title: "Affiliate Disclosure | LeTrusto",
    description:
      "Learn how LeTrusto handles affiliate relationships, commissions, and how they relate to our editorial recommendations.",
    url: "/affiliate-disclosure",
    siteName: "LeTrusto",
    type: "website",
  },
};

export default function AffiliateDisclosurePage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-14">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
        Transparency
      </p>
      <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950">
        Affiliate Disclosure
      </h1>
      <p className="mt-4 text-base leading-relaxed text-slate-600">
        LeTrusto is a software research and comparison platform. This page
        explains when and how we may earn affiliate commissions, and how those
        relationships relate to our editorial recommendations.
      </p>

      <div className="mt-10 space-y-8 text-sm leading-7 text-slate-700">

        <section>
          <h2 className="text-xl font-bold text-slate-900">
            What is an affiliate link?
          </h2>
          <p className="mt-3">
            An affiliate link is a tracked URL that identifies LeTrusto as the
            referral source when a user visits a provider&apos;s website. If you
            purchase a product or sign up for a subscription after clicking one
            of these links, the provider may pay LeTrusto a commission as a
            referral fee.
          </p>
          <p className="mt-3">
            <strong className="text-slate-900">
              You pay the same price either way.
            </strong>{" "}
            Affiliate commissions are paid by the provider, not added to your
            purchase price.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-slate-900">
            Which links are affiliate links?
          </h2>
          <p className="mt-3">
            Affiliate links on LeTrusto are limited to providers with whom we
            have a current, approved affiliate relationship. Links to providers
            without an active affiliate partnership are plain outbound links and
            generate no commission.
          </p>
          <p className="mt-3">
            Currently active affiliate partnerships:
          </p>
          <ul className="mt-3 space-y-2 pl-4">
            <li className="flex items-start gap-2">
              <span className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-purple-600" aria-hidden="true" />
              <span>
                <strong className="text-slate-900">ElevenLabs</strong> — AI
                voice and audio platform. We are an approved affiliate partner
                via PartnerStack. Affiliate links to ElevenLabs are clearly
                labelled on tool pages.
              </span>
            </li>
          </ul>
          <p className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-slate-600">
            We do not claim affiliate partnerships with providers that have not
            approved us. As new partnerships are confirmed, this page will be
            updated.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-slate-900">
            Does affiliate status affect our recommendations?
          </h2>
          <p className="mt-3">
            Affiliate relationships do not automatically determine
            recommendations, rankings, or ratings. Tools are evaluated based on
            their features, pricing, use-case fit, and verified data — not on
            whether an affiliate agreement exists.
          </p>
          <p className="mt-3">
            A tool with no affiliate relationship can appear at the top of a
            recommendation. A tool with an active affiliate agreement can
            receive a neutral or negative assessment when the evidence supports
            that.
          </p>
          <p className="mt-3">
            Editorial decisions are governed by our{" "}
            <Link
              href="/methodology"
              className="font-medium text-purple-700 underline underline-offset-2 hover:text-purple-900"
            >
              Research &amp; Editorial Methodology
            </Link>
            .
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-slate-900">
            How affiliate revenue is used
          </h2>
          <p className="mt-3">
            Commissions earned through qualifying affiliate purchases fund the
            operation and development of LeTrusto, including research,
            verification, platform infrastructure, and editorial work.
          </p>
          <p className="mt-3">
            LeTrusto does not charge users subscription or access fees. Affiliate
            revenue is the primary source of revenue for this platform.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-slate-900">
            Pricing and accuracy
          </h2>
          <p className="mt-3">
            Software pricing, features, and availability change frequently.
            While LeTrusto verifies data at regular intervals, information
            displayed on this site may not reflect the most current pricing or
            terms.
          </p>
          <p className="mt-3">
            Always verify final pricing, features, and subscription terms
            directly with the provider before completing a purchase.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-slate-900">Contact</h2>
          <p className="mt-3">
            If you have questions about our affiliate disclosures, discovered an
            inaccuracy, or want to discuss a partnership, please{" "}
            <Link
              href="/contact"
              className="font-medium text-purple-700 underline underline-offset-2 hover:text-purple-900"
            >
              contact us
            </Link>
            .
          </p>
        </section>

        <p className="text-xs text-slate-400">
          Last updated: 2026-08-10
        </p>
      </div>
    </main>
  );
}
