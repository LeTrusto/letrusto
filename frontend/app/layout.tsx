import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
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
  title: {
    default: "LeTrusto — Know Before You Buy",
    template: "%s | LeTrusto",
  },
  description:
    "LeTrusto is your AI Buying Advisor. Compare electronics, get personalised recommendations, track prices, and shop smarter.",
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
    title: "LeTrusto — AI Buying Advisor",
    description: "Compare electronics, get AI recommendations, and track price drops.",
    images: [{ url: "/images/og-default.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "LeTrusto — AI Buying Advisor",
    description: "Compare electronics, get AI recommendations, and track price drops.",
    images: ["/images/og-default.png"],
  },
  robots: { index: true, follow: true },
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
        <AuthProvider>
          <Navbar />
          {children}
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
