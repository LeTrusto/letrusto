import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import AffiliateDisclosure from "@/components/AffiliateDisclosure";
import GoogleAnalytics from "@/components/GoogleAnalytics";
import SchemaOrg from "@/components/SchemaOrg";
import { AuthProvider } from "@/lib/authContext";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
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
    "LeTrusto is an AI-powered buying advisor for AI tools and software recommendations.",
  keywords: [
    "AI tools",
    "software buying advisor",
    "AI software comparison",
    "AI recommendations",
    "buying guides",
    "research before buying",
    "know before you buy",
  ],
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://letrusto.com",
    siteName: "LeTrusto",
    title: "LeTrusto",
    description: "AI-powered buying advisor for AI tools and software.",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    site: "@letrusto",
    creator: "@letrusto",
    title: "LeTrusto",
    description: "AI-powered buying advisor for AI tools and software.",
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
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-gray-50 text-gray-900">
        <SchemaOrg
          type="WebSite"
          data={{
            "@id": "https://letrusto.com/#website",
            name: "LeTrusto",
            url: "https://letrusto.com",
            description: "AI-powered buying advisor for AI tools and software recommendations.",
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
            description: "Research-backed buying guidance for AI tools and software comparisons.",
            sameAs: ["https://x.com/letrusto", "https://instagram.com/letrusto"],
          }}
        />
        <AuthProvider>
          <Navbar />
          <AffiliateDisclosure />
          {children}
          <Footer />
        </AuthProvider>
        <GoogleAnalytics />
      </body>
    </html>
  );
}
