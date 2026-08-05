import type { Metadata } from "next";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
  title: "Report Issue",
  robots: {
    index: false,
    follow: true,
  },
  alternates: {
    canonical: "/support",
  },
};

export default function ReportIssuePage() {
  redirect("/support?tab=contact&category=report_broken");
}
