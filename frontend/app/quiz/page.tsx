import type { Metadata } from "next";

import WidgetQuiz from "@/components/saas/WidgetQuiz";

export const metadata: Metadata = {
  title: "Find Your Best Social Proof Widget",
  description: "Answer three questions to find the LeTrusto widget and plan that fit your business.",
  alternates: { canonical: "/quiz" },
};

export default function QuizPage() {
  return <WidgetQuiz />;
}
