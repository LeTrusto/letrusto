import type { Metadata } from "next";

import RegisterPage from "@/app/register/RegisterPage";

export const metadata: Metadata = {
  title: "Start Your LeTrusto Workspace",
  description: "Start a 14-day LeTrusto trial for your business social proof workspace.",
  alternates: { canonical: "/signup" },
};

export default function SignupPage() {
  return <RegisterPage />;
}