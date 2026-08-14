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
    "Discover trending beauty, jewellery and style finds at everyday prices. LeTrusto — curated discovery commerce for India.",
  keywords: [
    "beauty accessories",
    "fashion jewellery",
    "hair accessories",
    "style finds",
    "affordable fashion",
    "trending finds",
    "LeTrusto",
    "online shopping India",
  ],
  openGraph: {
    type: "website",
    locale: "en_IN",
    url: "https://letrusto.com",
    siteName: "LeTrusto",
    title: "LeTrusto — Trending Finds. Everyday Prices.",
    description: "Discover trending beauty, jewellery and style finds at everyday prices.",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    site: "@letrusto",
    creator: "@letrusto",
    title: "LeTrusto — Trending Finds. Everyday Prices.",
    description: "Discover trending beauty, jewellery and style finds at everyday prices.",
    images: ["/images/og-default.svg"],
  },
  authors: [{ name: "LeTrusto", url: "https://letrusto.com" }],
  creator: "LeTrusto",
  publisher: "LeTrusto",
  manifest: "/site.webmanifest",
  appleWebApp: {
    capable: true,
    title: "LeTrusto",
    statusBarStyle: "default",
  },
  icons: {
    icon: [
      { url: "/favicon.ico" },
      { url: "/favicon-32x32.png", type: "image/png", sizes: "32x32" },
      { url: "/favicon-16x16.png", type: "image/png", sizes: "16x16" },
    ],
    apple: [{ url: "/apple-touch-icon.png", type: "image/png", sizes: "180x180" }],
    shortcut: ["/favicon.ico"],
    other: [
      { rel: "mask-icon", url: "/safari-pinned-tab.svg", color: "#111827" },
    ],
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: "#ffffff",
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
        <body className="min-h-full flex flex-col bg-[var(--surface-soft)] text-[var(--text-primary)]">
        <SchemaOrg
          type="WebSite"
          data={{
            "@id": "https://letrusto.com/#website",
            name: "LeTrusto",
            url: "https://letrusto.com",
            description: "Curated discovery commerce for beauty, jewellery and style finds in India.",
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
              url: "https://letrusto.com/android-chrome-512x512.png",
              width: 512,
              height: 512,
            },
            description: "Curated discovery commerce for beauty, jewellery and style finds in India.",
            sameAs: ["https://x.com/letrusto", "https://instagram.com/letrusto"],
          }}
        />
        <AuthProvider>
          <CartProvider>
            <CommerceNavbar />
            <main className="flex-1 pb-16 md:pb-0">{children}</main>
            <CommerceFooter />
            <MobileNav />
          </CartProvider>
        </AuthProvider>
        <GoogleAnalytics />
      </body>
    </html>
  );
}
