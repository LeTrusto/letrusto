import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Geist_Mono } from "next/font/google";

import CommerceNavbar from "@/components/layout/CommerceNavbar";
import CommerceFooter from "@/components/layout/CommerceFooter";
import MobileNav from "@/components/layout/MobileNav";
import GoogleAnalytics from "@/components/GoogleAnalytics";
import SchemaOrg from "@/components/SchemaOrg";
import { AuthProvider } from "@/lib/authContext";
import { CartProvider } from "@/lib/cartContext";
import { ConsentProvider } from "@/lib/consentContext";
import CookieConsent from "@/components/CookieConsent";

import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://letrusto.com"),
  applicationName: "LeTrusto",
  alternates: {
    canonical: "/",
  },
  title: {
    default: "LeTrusto",
    template: "%s | LeTrusto",
  },
  description:
    "Custom apparel, wall art and accessories printed on demand for the current India launch. LeTrusto — unique designs, freshly printed.",
  keywords: [
    "print on demand",
    "custom t-shirts",
    "custom mugs",
    "wall art prints",
    "printed apparel",
    "custom phone cases",
    "unique designs",
    "India shipping",
    "LeTrusto",
    "made to order",
  ],
  openGraph: {
    type: "website",
    locale: "en",
    url: "https://letrusto.com",
    siteName: "LeTrusto",
    title: "LeTrusto — Unique Designs. Freshly Printed.",
    description: "Custom apparel, wall art and accessories printed on demand for the current India launch.",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    site: "@letrusto",
    creator: "@letrusto",
    title: "LeTrusto — Unique Designs. Freshly Printed.",
    description: "Custom apparel, wall art and accessories printed on demand for the current India launch.",
    images: ["/images/og-default.svg"],
  },
  authors: [{ name: "LeTrusto", url: "https://letrusto.com" }],
  creator: "LeTrusto",
  publisher: "LeTrusto",
  manifest: "/site.webmanifest",
  icons: {
    icon: "/letrusto-icon.svg",
    shortcut: "/letrusto-icon.svg",
    apple: "/letrusto-icon.svg",
  },
  appleWebApp: {
    capable: true,
    title: "LeTrusto",
    statusBarStyle: "default",
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: "#ECECFC",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${geistMono.variable} h-full antialiased`}
    >
        <body className="min-h-full flex flex-col bg-[var(--background)] text-[var(--text-primary)]">
        <SchemaOrg
          type="WebSite"
          data={{
            "@id": "https://letrusto.com/#website",
            name: "LeTrusto",
            url: "https://letrusto.com",
            description: "Original designs printed on demand for the current India launch.",
            potentialAction: {
              "@type": "SearchAction",
              target: "https://letrusto.com/search?q={search_term_string}",
              "query-input": "required name=search_term_string",
            },
          }}
        />
        <SchemaOrg
          type="Organization"
          data={{
            "@id": "https://letrusto.com/#organization",
            name: "LeTrusto",
            url: "https://letrusto.com",
            logo: {
              "@type": "ImageObject",
              url: "https://letrusto.com/LeTrusto%20Brand%20Logo.png",
              width: 1774,
              height: 887,
            },
            description: "Original designs printed on demand for the current India launch.",
            sameAs: ["https://x.com/letrusto", "https://instagram.com/letrusto"],
          }}
        />
        <ConsentProvider>
          <AuthProvider>
            <CartProvider>
            <CommerceNavbar />
            <main className="flex-1 pb-16 lg:pb-0">{children}</main>
            <CommerceFooter />
            <MobileNav />
            </CartProvider>
          </AuthProvider>
          <CookieConsent />
          <GoogleAnalytics />
        </ConsentProvider>
      </body>
    </html>
  );
}
