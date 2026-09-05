import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Geist_Mono } from "next/font/google";

import CommerceShell from "@/components/layout/CommerceShell";
import FunnelAnalytics from "@/components/FunnelAnalytics";
import GoogleAnalytics from "@/components/GoogleAnalytics";
import SchemaOrg from "@/components/SchemaOrg";
import { AuthProvider } from "@/lib/authContext";
import { CartProvider } from "@/lib/cartContext";
import { ConsentProvider } from "@/lib/consentContext";
import CookieConsent from "@/components/CookieConsent";
import { SITE_URL } from "@/config/site";

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
  metadataBase: new URL(SITE_URL),
  applicationName: "LeTrusto",
  alternates: {
    canonical: "/",
  },
  title: {
    default: "LeTrusto",
    template: "%s | LeTrusto",
  },
  description:
    "Practical digital tools, templates and services for Indian businesses. LeTrusto is building the next chapter of useful digital commerce.",
  keywords: [
    "digital tools",
    "business templates",
    "business services India",
    "digital products India",
    "LeTrusto",
  ],
  openGraph: {
    type: "website",
    locale: "en",
    url: SITE_URL,
    siteName: "LeTrusto",
    title: "LeTrusto — Digital tools and services",
    description: "Practical digital tools, templates and services for Indian businesses.",
    images: [{ url: "/og-card.png", width: 1254, height: 1254 }],
  },
  twitter: {
    card: "summary_large_image",
    site: "@letrusto",
    creator: "@letrusto",
    title: "LeTrusto — Digital tools and services",
    description: "Practical digital tools, templates and services for Indian businesses.",
    images: ["/og-card.png"],
  },
  authors: [{ name: "LeTrusto", url: SITE_URL }],
  creator: "LeTrusto",
  publisher: "LeTrusto",
  manifest: "/site.webmanifest",
  icons: {
    icon: [
      { url: "/favicon.ico", type: "image/x-icon" },
      { url: "/favicon-192x192.png", sizes: "192x192", type: "image/png" },
    ],
    shortcut: "/favicon.ico",
    apple: "/apple-touch-icon.png",
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
            "@id": `${SITE_URL}/#website`,
            name: "LeTrusto",
            url: SITE_URL,
            description: "Practical digital tools, templates and services for Indian businesses.",
            potentialAction: {
              "@type": "SearchAction",
              target: `${SITE_URL}/search?q={search_term_string}`,
              "query-input": "required name=search_term_string",
            },
          }}
        />
        <SchemaOrg
          type="Organization"
          data={{
            "@id": `${SITE_URL}/#organization`,
            name: "LeTrusto",
            url: SITE_URL,
            logo: {
              "@type": "ImageObject",
              url: `${SITE_URL}/LeTrusto%20Brand%20Logo.png`,
              width: 1774,
              height: 887,
            },
            description: "Practical digital tools, templates and services for Indian businesses.",
            sameAs: ["https://x.com/letrusto", "https://instagram.com/letrusto"],
          }}
        />
        <ConsentProvider>
          <AuthProvider>
            <CartProvider>
            <CommerceShell>{children}</CommerceShell>
            </CartProvider>
          </AuthProvider>
          <CookieConsent />
          <GoogleAnalytics />
          <FunnelAnalytics />
        </ConsentProvider>
      </body>
    </html>
  );
}
