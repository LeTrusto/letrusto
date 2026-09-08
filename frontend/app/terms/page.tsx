import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms of Service",
  description: "Review the terms governing use of the LeTrusto social proof platform.",
  alternates: { canonical: "/terms" },
};

const sections = [
  {
    title: "1. User Account Terms",
    body: [
      "You may use LeTrusto only if you can form a binding agreement and are authorized to act for the business or organization represented by your workspace. Keep account credentials, API keys, and workspace access secure.",
      "You are responsible for the accuracy and lawfulness of information sent to LeTrusto, for activity under your account, and for ensuring that connected event data is collected and displayed with the required permissions and notices.",
    ],
  },
  {
    title: "2. Subscription Billing and Renewal",
    body: [
      "LeTrusto plans, included usage, limits, and features are shown in the workspace or applicable order page. A paid subscription begins when the selected plan is activated and continues for the billing period shown at checkout or in the workspace.",
      "Unless cancelled before the renewal date, a paid subscription renews for the same billing period. You authorize the applicable payment provider to charge the selected payment method for recurring renewals, taxes, and permitted adjustments. You can manage or cancel renewal from your workspace or by contacting support.",
      "Plan changes may affect included usage immediately or at the next renewal, as shown when the change is confirmed. We may suspend paid features for failed or overdue payments after providing reasonable notice where practical.",
    ],
  },
  {
    title: "3. Acceptable Use Policy",
    body: [
      "You must not use LeTrusto to break the law, violate privacy or publicity rights, transmit malicious code, probe or bypass security controls, overload the service, reverse engineer protected systems, or access another workspace without authorization.",
      "You must not create misleading social proof, fabricate customer activity, impersonate customers, manipulate reviews, or use the platform to deceive visitors. We may remove content, restrict features, or suspend access when reasonably necessary to protect users, customers, or the service.",
    ],
  },
  {
    title: "4. Customer Content and Platform Rights",
    body: [
      "You retain rights in content and event data that you submit. You grant LeTrusto the limited rights needed to host, process, display, secure, and improve the service according to your configuration and these terms.",
      "LeTrusto owns its software, interfaces, documentation, trademarks, and service technology. These terms do not transfer ownership of LeTrusto intellectual property to you.",
    ],
  },
  {
    title: "5. Service Availability and Limitation of Liability",
    body: [
      "We work to keep LeTrusto reliable, but the service may be affected by maintenance, provider outages, network failures, security incidents, or events outside our reasonable control. Features and limits may change as the platform develops.",
      "To the maximum extent permitted by law, LeTrusto is not liable for indirect, incidental, special, consequential, or exemplary loss, or for loss of profits, revenue, data, goodwill, or business interruption arising from use of the service. Our aggregate liability for a claim relating to the service will not exceed the fees paid by you for the service during the twelve months before the event giving rise to the claim, except where applicable law requires otherwise.",
    ],
  },
  {
    title: "6. Termination and Updates",
    body: [
      "You may stop using the service or cancel a subscription according to the plan terms. We may suspend or terminate access for material breach, unlawful use, security risk, non-payment, or where required to protect the service and its users.",
      "We may update these terms as the product or law changes. Material updates will be communicated through the service or by email where appropriate. Continued use after the effective date means you accept the updated terms.",
    ],
  },
];

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-[var(--background)] px-5 py-14 sm:px-8 lg:px-12 lg:py-20">
      <article className="mx-auto max-w-4xl">
        <p className="text-xs font-bold uppercase tracking-[0.22em] text-[var(--lt-primary)]">LeTrusto policies</p>
        <h1 className="mt-3 text-4xl font-black tracking-tight text-[var(--text-primary)] md:text-6xl">Terms of Service</h1>
        <p className="mt-4 text-sm text-[var(--text-muted)]">Last updated: September 8, 2026</p>
        <p className="mt-8 max-w-3xl text-base leading-8 text-[var(--text-secondary)]">These terms govern access to and use of LeTrusto, a B2B SaaS platform for collecting, managing, and displaying customer social proof.</p>
        <div className="mt-12 space-y-10">
          {sections.map((section) => (
            <section key={section.title} className="border-t border-[var(--border)] pt-6">
              <h2 className="text-xl font-bold text-[var(--text-primary)]">{section.title}</h2>
              <div className="mt-3 space-y-3 text-sm leading-7 text-[var(--text-secondary)]">{section.body.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div>
            </section>
          ))}
        </div>
        <p className="mt-12 border-t border-[var(--border)] pt-6 text-sm leading-7 text-[var(--text-secondary)]">Questions about these terms? Email <a className="font-semibold text-[var(--lt-primary)] underline hover:text-amber-500" href="mailto:support@letrusto.com">support@letrusto.com</a> or visit <Link className="font-semibold text-[var(--lt-primary)] underline hover:text-amber-500" href="/support">Contact Support</Link>.</p>
      </article>
    </main>
  );
}
