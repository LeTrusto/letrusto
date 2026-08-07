import type { Metadata } from "next";

import RegisterPage from "./RegisterPage";

export const metadata: Metadata = {
  title: "Create Account",
  description: "Create your free LeTrusto account to save products, comparisons, and alerts.",
  robots: {
    index: false,
    follow: false,
  },
  alternates: {
    canonical: "/register",
  },
};

export default function Page() {
  return <RegisterPage />;
}

