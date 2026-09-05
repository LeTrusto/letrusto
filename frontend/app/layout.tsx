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

const SITE_DESCRIPTION = "LeTrusto helps growing businesses collect, manage, and display customer reviews and social proof with lightweight widgets.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  applicationName: "LeTrusto",
  alternates: {
    canonical: "/",
  },
  title: {
    default: "LeTrusto - Social Proof Widgets for Growing Businesses",
    template: "%s | LeTrusto",
  },
  description: SITE_DESCRIPTION,
  keywords: [
    "social proof widgets",
    "customer reviews",
    "review widgets",
    "customer testimonials",
    "LeTrusto",
  ],
  openGraph: {
    type: "website",
    locale: "en",
    url: SITE_URL,
    siteName: "LeTrusto",
    title: "LeTrusto",
    description: SITE_DESCRIPTION,
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
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
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
            description: SITE_DESCRIPTION,
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
              url: `${SITE_URL}/logo.png`,
              width: 2008,
              height: 783,
            },
            description: SITE_DESCRIPTION,
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
