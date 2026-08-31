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
      <p className="mt-3 text-sm text-gray-500">Last updated: 2026-08-31</p>

      <div className="mt-8 space-y-6 text-sm leading-7 text-gray-700">
        <section>
          <h2 className="text-lg font-bold text-gray-900">1. Information We Collect</h2>
          <p>We collect information you provide when creating an account, placing an order, using checkout, contacting support, or requesting updates. This may include your name, email address, phone number, delivery address, order information, selected products and variants, payment status, provider order identifiers, support messages, and cookie-consent preferences.</p>
          <p className="mt-3">LeTrusto uses email and password authentication. Passwords are handled through the authentication system and are not displayed to LeTrusto staff in plain text.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">2. How We Use Data</h2>
          <p>We use customer data to create and manage accounts, calculate checkout totals, process orders, arrange fulfillment and delivery, provide customer support, send transactional updates, maintain account security, prevent misuse, improve the storefront, and keep records needed to operate the business.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">3. Third-Party Services</h2>
          <p>We share information with service providers only where needed for the service they provide. Razorpay processes active checkout payments. Printful receives the order and delivery details needed to produce and ship made-to-order products. Resend may be used for transactional email delivery. LeTrusto is hosted using application infrastructure providers used by the frontend and backend deployments.</p>
          <p className="mt-3">Payment credentials such as full card details are handled by Razorpay. LeTrusto stores order, payment status, and provider identifiers needed to verify and support orders, but does not store full card credentials.</p>
          <p className="mt-3">We do not sell personal information.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">4. Cookies</h2>
          <p>Essential browser storage keeps sign-in, cart, checkout, payment, consent, and security features working. LeTrusto stores a versioned cookie-consent preference so your choices can be remembered and changed later.</p>
          <p className="mt-3">Analytics is optional. Google Analytics loads only after analytics consent is granted, and analytics can be revoked through Cookie Preferences. Marketing is a separate consent category, but no marketing tools are currently configured.</p>
          <CookiePreferencesLink />
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">5. Security and Retention</h2>
          <p>We use reasonable technical and organizational measures to protect customer information. No online service can guarantee absolute security.</p>
          <p className="mt-3">We keep account, order, support, and operational records for as long as needed to provide the service, support customers, resolve disputes, prevent misuse, and meet business or legal record-keeping needs. Exact retention periods may vary by record type and business requirements.</p>
        </section>
        <section>
          <h2 className="text-lg font-bold text-gray-900">6. Privacy Requests and Contact</h2>
          <p>Questions about privacy or requests concerning your personal information can be sent to <a className="underline" href="mailto:hello@letrusto.com">hello@letrusto.com</a> or through the <a className="underline" href="/support?tab=contact&category=contact">Support Centre</a>.</p>
        </section>
      </div>
    </main>
  );
}
