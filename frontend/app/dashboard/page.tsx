import type { Metadata } from "next";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
  title: "Trust Studio",
  description: "Manage LeTrusto social proof widgets and customer events.",
  robots: {
    index: false,
    follow: false,
  },
};

export const dynamic = "force-dynamic";

export default function DashboardPage() {
  redirect("/dashboard/widgets");
}
