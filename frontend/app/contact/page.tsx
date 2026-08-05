import type { Metadata } from "next";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
  title: "Contact",
  robots: {
    index: false,
    follow: true,
  },
  alternates: {
    canonical: "/support",
  },
};

export default function ContactPage() {
  redirect("/support?tab=contact&category=contact");
}
