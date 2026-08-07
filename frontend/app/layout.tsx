import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
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
  title: {
    default: "LeTrusto",
    template: "%s | LeTrusto",
  },
  description:
    "LeTrusto helps people compare products, discover trusted recommendations, and buy with confidence.",
  keywords: [
    "AI buying advisor",
    "electronics comparison",
    "product reviews",
    "price tracker",
    "best smartphones",
    "best laptops",
    "India shopping",
  ],
  openGraph: {
    type: "website",
    locale: "en_IN",
    url: "https://letrusto.com",
    siteName: "LeTrusto",
    title: "LeTrusto",
    description: "Compare products, get AI recommendations, and shop with confidence.",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "LeTrusto",
    description: "Compare products, get AI recommendations, and shop with confidence.",
    images: ["/images/og-default.svg"],
  },
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
            name: "LeTrusto",
            url: "https://letrusto.com",
            description: "AI Buying Advisor — Compare electronics, get personalised recommendations, track prices.",
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
            name: "LeTrusto",
            url: "https://letrusto.com",
            logo: "https://letrusto.com/images/logo/logo.png",
            description: "Research-backed buying guidance with product comparisons, recommendations, and editorial clarity.",
            sameAs: ["https://twitter.com/letrusto", "https://instagram.com/letrusto"],
          }}
        />
        <AuthProvider>
          <Navbar />
          {children}
          <Footer />
        </AuthProvider>
        <GoogleAnalytics />
      </body>
    </html>
  );
}
