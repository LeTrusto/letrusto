import type { Metadata } from "next";
import CookiePreferencesLink from "@/components/CookiePreferencesLink";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Read how LeTrusto collects, uses, and protects your data.",
  alternates: {
    canonical: "/privacy-policy",
  },
};

export default function PrivacyPolicyPage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-4xl font-black text-gray-900">Privacy Policy</h1>
      <p className="mt-3 text-sm text-gray-500">Last updated: 2026-08-26</p>

      <div className="mt-8 space-y-6 text-sm leading-7 text-gray-700">
        <section>
          <h2 className="text-lg font-bold text-gray-900">1. Information We Collect</h2>
          <p>We collect the information you provide when creating an account, placing an order, contacting support, or signing up for updates. This may include your name, email address, phone number, delivery address, order details, and payment status. Payment credentials are processed by our payment providers and are not stored by LeTrusto.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">2. How We Use Data</h2>
          <p>We use data to process and deliver orders, provide customer support, send transactional updates, maintain account security, improve the storefront, and meet legal and accounting obligations.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">3. Third-Party Services</h2>
          <p>We use service providers for hosting, authentication, analytics, email, payments, and order fulfillment. They receive only the information needed to provide their service. We do not sell personal information.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">4. Cookies</h2>
          <p>Essential storage keeps sign-in, cart, checkout, payment, and security features working. Optional analytics is used only after permission. No marketing tools are currently configured.</p>
          <CookiePreferencesLink />
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">5. Contact</h2>
          <p>Questions about privacy or requests concerning your personal information can be sent through our <a className="underline" href="/contact">Contact page</a>.</p>
        </section>
      </div>
    </main>
  );
}
