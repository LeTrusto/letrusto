"use client";

import { ArrowLeft, ArrowRight, Check, Loader2, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

import { trackSafeEvent } from "@/lib/analytics";
import { captureWidgetQuizLead, recordMarketingEvent } from "@/services/marketing.service";

type Choice = { value: string; label: string; detail: string };
type Answers = { businessType: string; primaryGoal: string; monthlyVisitors: string };

type Recommendation = {
  key: string;
  name: string;
  plan: string;
  summary: string;
  reason: string;
};

const steps: Array<{ key: keyof Answers; eyebrow: string; title: string; choices: Choice[] }> = [
  {
    key: "businessType",
    eyebrow: "Step 1 of 3",
    title: "What kind of business are you growing?",
    choices: [
      { value: "store", label: "Online store", detail: "Products, subscriptions, or ecommerce" },
      { value: "service", label: "Service business", detail: "Agencies, consultants, or bookings" },
      { value: "saas", label: "SaaS or digital product", detail: "Software, apps, or digital tools" },
      { value: "creator", label: "Creator or community", detail: "Audience-led offers and memberships" },
    ],
  },
  {
    key: "primaryGoal",
    eyebrow: "Step 2 of 3",
    title: "What should your proof do next?",
    choices: [
      { value: "increase_sales", label: "Create purchase momentum", detail: "Show recent activity at the right moment" },
      { value: "collect_reviews", label: "Collect better reviews", detail: "Turn customer feedback into usable proof" },
      { value: "showcase_testimonials", label: "Showcase customer stories", detail: "Build a polished library of trust" },
    ],
  },
  {
    key: "monthlyVisitors",
    eyebrow: "Step 3 of 3",
    title: "How many people visit you each month?",
    choices: [
      { value: "under_1000", label: "Under 1,000", detail: "I am proving the first channel" },
      { value: "1000_10000", label: "1,000 to 10,000", detail: "I have a growing audience" },
      { value: "over_10000", label: "More than 10,000", detail: "I need proof at scale" },
    ],
  },
];

function getRecommendation(answers: Answers): Recommendation {
  const widget = answers.primaryGoal === "collect_reviews"
    ? { key: "review_collection", name: "Review Collection", summary: "Capture feedback while the customer experience is still fresh.", reason: "Your priority is turning customer feedback into a repeatable trust asset." }
    : answers.primaryGoal === "showcase_testimonials"
      ? { key: "wall_of_love", name: "Wall of Love", summary: "Give your strongest customer stories a home visitors can explore.", reason: "Your visitors need a richer proof layer before they commit." }
      : { key: "sales_popups", name: "Live Sales Popups", summary: "Show lightweight activity signals without slowing down your site.", reason: "Visible momentum is the fastest proof layer for your current goal." };
  const plan = answers.monthlyVisitors === "over_10000" ? "Pro" : answers.monthlyVisitors === "1000_10000" ? "Starter" : "Free";
  return { ...widget, plan };
}

export default function WidgetQuiz() {
  const [stepIndex, setStepIndex] = useState(0);
  const [answers, setAnswers] = useState<Answers>({ businessType: "", primaryGoal: "", monthlyVisitors: "" });
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [consented, setConsented] = useState(true);
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    trackSafeEvent("widget_quiz_started", { source: "quiz_page" });
    void recordMarketingEvent("widget_quiz_started", { source: "quiz_page" }).catch(() => undefined);
  }, []);

  const currentStep = steps[stepIndex];
  const selectedValue = currentStep ? answers[currentStep.key] : "";

  function choose(value: string) {
    if (!currentStep) return;
    const nextAnswers = { ...answers, [currentStep.key]: value };
    setAnswers(nextAnswers);
    if (stepIndex < steps.length - 1) {
      setStepIndex((current) => current + 1);
      return;
    }
    const result = getRecommendation(nextAnswers);
    setRecommendation(result);
    trackSafeEvent("widget_quiz_completed", { recommended_widget: result.key, recommended_plan: result.plan });
    void recordMarketingEvent("widget_quiz_completed", { recommended_widget: result.key, recommended_plan: result.plan }).catch(() => undefined);
  }

  async function submitLead(event: React.FormEvent) {
    event.preventDefault();
    if (!recommendation) return;
    setSubmitting(true);
    setError("");
    try {
      await captureWidgetQuizLead({
        email,
        full_name: fullName || undefined,
        business_type: answers.businessType,
        primary_goal: answers.primaryGoal,
        monthly_visitors: answers.monthlyVisitors,
        recommended_widget: recommendation.key,
        consented_to_updates: consented,
      });
      setSubmitted(true);
      trackSafeEvent("widget_quiz_lead_captured", { recommended_widget: recommendation.key, recommended_plan: recommendation.plan });
      void recordMarketingEvent("widget_quiz_lead_captured", { recommended_widget: recommendation.key, recommended_plan: recommendation.plan }).catch(() => undefined);
    } catch {
      setError("We could not save your recommendation. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  function restart() {
    setStepIndex(0);
    setAnswers({ businessType: "", primaryGoal: "", monthlyVisitors: "" });
    setRecommendation(null);
    setSubmitted(false);
    setEmail("");
    setFullName("");
    setError("");
  }

  return (
    <main className="min-h-[calc(100vh-72px)] bg-[#f7faf8] px-5 py-12 text-[#17382e] sm:px-8 sm:py-20">
      <section className="mx-auto max-w-3xl">
        <div className="text-center"><span className="inline-flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.22em] text-[#2563eb]"><Sparkles size={14} /> LeTrusto fit finder</span><h1 className="mt-5 text-4xl font-black tracking-tight sm:text-6xl">Find the proof layer your business needs.</h1><p className="mx-auto mt-5 max-w-xl text-base leading-7 text-[#587268]">Answer three quick questions and get a practical widget recommendation for your next growth stage.</p></div>
        <div className="mt-10 border border-[#d9e5df] bg-white p-5 shadow-[0_20px_60px_rgba(23,56,46,0.08)] sm:p-9">
          {recommendation ? (
            submitted ? <div className="py-8 text-center"><span className="mx-auto flex h-12 w-12 items-center justify-center bg-[#17382e] text-white"><Check /></span><h2 className="mt-6 text-2xl font-black">Your recommendation is saved.</h2><p className="mx-auto mt-3 max-w-md text-sm leading-6 text-[#587268]">Start with {recommendation.name} on the {recommendation.plan} plan. We will use your answers to keep future guidance relevant.</p><button type="button" onClick={restart} className="mt-7 border border-[#17382e] px-4 py-3 text-sm font-bold hover:bg-[#17382e] hover:text-white">Run the finder again</button></div> : <div><p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#2563eb]">Your recommendation</p><h2 className="mt-3 text-3xl font-black">{recommendation.name}</h2><p className="mt-3 text-base leading-7 text-[#587268]">{recommendation.summary}</p><p className="mt-5 border-l-2 border-[#2563eb] pl-4 text-sm leading-6 text-[#39564c]">{recommendation.reason}</p><div className="mt-7 border border-[#d9e5df] bg-[#f7faf8] p-5"><p className="text-xs font-bold uppercase tracking-[0.16em] text-[#71877f]">Best starting plan</p><p className="mt-2 text-xl font-black">{recommendation.plan}</p><p className="mt-1 text-sm text-[#587268]">Install your first widget and learn which proof format earns attention.</p></div><form onSubmit={(event) => { void submitLead(event); }} className="mt-8 space-y-4"><div><label htmlFor="quiz-name" className="mb-2 block text-sm font-bold">Name <span className="font-normal text-[#71877f]">(optional)</span></label><input id="quiz-name" value={fullName} onChange={(event) => setFullName(event.target.value)} className="h-12 w-full border border-[#cbdad2] bg-white px-3 outline-none focus:border-[#2563eb]" placeholder="Your name" /></div><div><label htmlFor="quiz-email" className="mb-2 block text-sm font-bold">Work email</label><input id="quiz-email" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} className="h-12 w-full border border-[#cbdad2] bg-white px-3 outline-none focus:border-[#2563eb]" placeholder="you@company.com" /></div><label className="flex items-start gap-3 text-sm leading-5 text-[#587268]"><input type="checkbox" checked={consented} onChange={(event) => setConsented(event.target.checked)} className="mt-1" /> Send me occasional product guidance and growth ideas. You can unsubscribe anytime.</label>{error && <p role="alert" className="text-sm font-semibold text-[#be123c]">{error}</p>}<div className="flex flex-wrap items-center justify-between gap-3"><button type="button" onClick={() => { setRecommendation(null); setStepIndex(steps.length - 1); }} className="inline-flex items-center gap-2 px-1 py-3 text-sm font-bold text-[#587268] hover:text-[#17382e]"><ArrowLeft size={16} /> Edit answers</button><button type="submit" disabled={submitting} className="inline-flex items-center gap-2 bg-[#2563eb] px-5 py-3 text-sm font-bold text-white hover:bg-blue-600 disabled:opacity-60">{submitting ? <Loader2 size={16} className="animate-spin" /> : <ArrowRight size={16} />}{submitting ? "Saving..." : "Save my recommendation"}</button></div></form></div>
          ) : <div><div className="mb-8 flex items-center justify-between gap-4"><p className="text-xs font-bold uppercase tracking-[0.16em] text-[#71877f]">{currentStep.eyebrow}</p><p className="text-xs font-semibold text-[#71877f]">{stepIndex + 1} / {steps.length}</p></div><h2 className="text-2xl font-black sm:text-3xl">{currentStep.title}</h2><div className="mt-7 grid gap-3">{currentStep.choices.map((choice) => <button key={choice.value} type="button" onClick={() => choose(choice.value)} className={`group flex items-center justify-between gap-4 border p-4 text-left transition ${selectedValue === choice.value ? "border-[#2563eb] bg-[#eff6ff]" : "border-[#d9e5df] hover:border-[#2563eb] hover:bg-[#f7faf8]"}`}><span><span className="block text-sm font-black">{choice.label}</span><span className="mt-1 block text-xs leading-5 text-[#71877f]">{choice.detail}</span></span><ArrowRight size={17} className="shrink-0 text-[#2563eb] transition-transform group-hover:translate-x-1" /></button>)}</div>{stepIndex > 0 && <button type="button" onClick={() => setStepIndex((current) => current - 1)} className="mt-6 inline-flex items-center gap-2 text-sm font-bold text-[#587268] hover:text-[#17382e]"><ArrowLeft size={16} /> Back</button>}</div>}
        </div>
      </section>
    </main>
  );
}
