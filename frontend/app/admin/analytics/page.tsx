import type { Metadata } from "next";
import AdminAnalyticsView from "./AdminAnalyticsView";

export const metadata: Metadata = {
  title: "Analytics | Admin",
  robots: { index: false, follow: false },
};

export default function AdminAnalyticsPage() {
  return <AdminAnalyticsView />;
}
