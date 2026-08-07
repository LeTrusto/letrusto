import type { Metadata } from "next";

import LoginPage from "./LoginPage";

export const metadata: Metadata = {
  title: "Sign In",
  description: "Sign in to your LeTrusto account to view your saved products and alerts.",
  robots: {
    index: false,
    follow: false,
  },
  alternates: {
    canonical: "/login",
  },
};

export default function Page() {
  return <LoginPage />;
}

