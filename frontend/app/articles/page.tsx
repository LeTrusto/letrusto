import type { Metadata } from "next";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
  title: "Buying Guides",
  robots: {
    index: false,
    follow: false,
  },
  alternates: {
    canonical: "/guides",
  },
};

export default function ArticlesPage() {
  redirect("/guides");
}
