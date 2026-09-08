import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Learn how LeTrusto collects, protects, and processes account and social proof data.",
  alternates: { canonical: "/privacy" },
};

const sections = [
  {
    title: "1. Data Collection",
    body: [
      "LeTrusto collects the information needed to create and secure your account, including your name, work email, authentication details, workspace settings, and support messages.",
      "When you use a LeTrusto widget, the platform may process approved event streams such as sign-ups, purchases, bookings, reviews, and other customer activity that you choose to connect. Visitor logs may include widget views, approximate location derived from technical data, browser and device information, timestamps, referral context, and interaction events.",
      "You control which customer events are approved for display. Do not send sensitive personal data, payment credentials, passwords, or information that your organization is not authorized to process.",
    ],
  },
  {
    title: "2. How We Use Data",
    body: [
      "We use data to provide, secure, maintain, and improve the LeTrusto workspace, deliver public widgets, measure widget usage, enforce plan limits, provide support, prevent abuse, and communicate service updates.",
      "We use aggregated or de-identified information for product analytics and reliability work where it cannot reasonably be used to identify an individual.",
    ],
  },
  {
    title: "3. Data Protection",
    body: [
      "LeTrusto uses access controls, authenticated APIs, encrypted connections, and operational safeguards designed to protect account, workspace, event, and visitor data. Access is limited according to role and service need.",
      "No online service can guarantee absolute security. You are responsible for protecting account credentials, API keys, and the data you send to your workspace. Notify support promptly if you suspect unauthorized access.",
    ],
  },
  {
    title: "4. Third-Party Processing",
    body: [
      "We use infrastructure, email delivery, analytics, authentication, and monitoring providers to operate LeTrusto. These providers process information only as needed to provide services to LeTrusto and under appropriate contractual or technical safeguards.",
      "A customer who installs a public widget remains responsible for its own notices, lawful basis, consent choices, and privacy commitments relating to visitor data collected through its website. LeTrusto does not sell personal information.",
    ],
  },
  {
    title: "5. GDPR and Compliance",
    body: [
      "Depending on the relationship and data involved, LeTrusto may act as a processor for customer-controlled event and visitor data, and as a controller for account, billing, support, and product administration data. Customers are responsible for determining their lawful basis and providing required notices to their users.",
      "Where GDPR or similar privacy laws apply, individuals may have rights to access, correct, delete, restrict, object to, or export personal data, subject to applicable exceptions. Send requests to support@letrusto.com with enough detail for us to identify the relevant workspace.",
      "We retain information for as long as needed to provide the service, meet contractual and legal duties, resolve disputes, prevent misuse, and maintain appropriate operational records. Retention may vary by data category.",
    ],
  },
];

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-[var(--background)] px-5 py-14 sm:px-8 lg:px-12 lg:py-20">
      <article className="mx-auto max-w-4xl">
        <p className="text-xs font-bold uppercase tracking-[0.22em] text-[var(--lt-primary)]">LeTrusto policies</p>
        <h1 className="mt-3 text-4xl font-black tracking-tight text-[var(--text-primary)] md:text-6xl">Privacy Policy</h1>
        <p className="mt-4 text-sm text-[var(--text-muted)]">Last updated: September 8, 2026</p>
        <p className="mt-8 max-w-3xl text-base leading-8 text-[var(--text-secondary)]">This policy explains how LeTrusto handles the account, event, visitor, and support information used to operate our B2B social proof platform.</p>
        <div className="mt-12 space-y-10">
          {sections.map((section) => (
            <section key={section.title} className="border-t border-[var(--border)] pt-6">
              <h2 className="text-xl font-bold text-[var(--text-primary)]">{section.title}</h2>
              <div className="mt-3 space-y-3 text-sm leading-7 text-[var(--text-secondary)]">{section.body.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div>
            </section>
          ))}
        </div>
        <p className="mt-12 border-t border-[var(--border)] pt-6 text-sm leading-7 text-[var(--text-secondary)]">Questions about privacy? Email <a className="font-semibold text-[var(--lt-primary)] underline hover:text-amber-500" href="mailto:support@letrusto.com">support@letrusto.com</a> or visit <Link className="font-semibold text-[var(--lt-primary)] underline hover:text-amber-500" href="/support">Contact Support</Link>.</p>
      </article>
    </main>
  );
}
