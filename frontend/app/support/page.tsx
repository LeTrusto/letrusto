import type { Metadata } from "next";
import SchemaOrg from "@/components/SchemaOrg";
import SupportPage from "./SupportPage";

export const metadata: Metadata = {
  title: "Support Centre",
  description: "Get help with LeTrusto — FAQ, contact us, report issues, and submit feedback.",
  alternates: {
    canonical: "/support",
  },
  openGraph: {
    title: "Support Centre",
    description: "Get help with LeTrusto — FAQ, contact us, report issues, and submit feedback.",
    url: "/support",
    siteName: "LeTrusto",
    type: "website",
    images: [{ url: "/images/og-default.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Support Centre",
    description: "Get help with LeTrusto — FAQ, contact us, report issues, and submit feedback.",
    images: ["/images/og-default.svg"],
  },
};

export default function SupportPageRoute() {
  const faqItems = [
    {
      question: "How can I contact LeTrusto support?",
      answer: "Use the Contact and Report tab to submit a support ticket and our team will respond by email.",
    },
    {
      question: "How long does support usually take?",
      answer: "Most support responses are handled within 24 to 48 hours depending on ticket volume.",
    },
    {
      question: "Can I report incorrect product information?",
      answer: "Yes. Choose the appropriate report category when submitting your support request.",
    },
  ];

  return (
    <>
      <SchemaOrg
        type="WebPage"
        data={{
          name: "Support Centre",
          url: "https://letrusto.com/support",
          description: "Get help with LeTrusto — FAQ, contact us, report issues, and submit feedback.",
        }}
      />
      <SchemaOrg
        type="FAQPage"
        data={{
          mainEntity: faqItems.map((item) => ({
            "@type": "Question",
            name: item.question,
            acceptedAnswer: {
              "@type": "Answer",
              text: item.answer,
            },
          })),
        }}
      />
      <SupportPage />
    </>
  );
}
