import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, BarChart3, Code2, Palette, Play } from "lucide-react";

export const metadata: Metadata = {
  title: "How It Works",
  description: "See how LeTrusto connects customer events to real-time social proof for growing businesses.",
  alternates: { canonical: "/how-it-works" },
};

const STEPS = [
  {
    icon: Code2,
    title: "Connect Your Events",
    description: "Integrate your storefront, webhooks, or CRM in minutes using our lightweight script.",
  },
  {
    icon: Palette,
    title: "Curate & Customise",
    description: "Tailor design, colors, triggers, and display rules to match your brand style natively.",
  },
  {
    icon: Play,
    title: "Go Live & Automate",
    description: "Automatically display real-time sales notifications, reviews, and sign-ups.",
  },
  {
    icon: BarChart3,
    title: "Analyze & Optimize",
    description: "Track visitor conversion lift and iterate on high-converting social proof signals.",
  },
];

export default function HowItWorksPage() {
  return (
    <main className="bg-[var(--background)]">
      <section className="mx-auto max-w-5xl px-5 py-14 md:px-6 md:py-20">
        <p className="text-center text-xs font-bold uppercase tracking-[0.24em] text-[var(--lt-primary)]">Trust Studio workflow</p>
        <h1 className="mt-3 text-center text-3xl font-black tracking-tight text-[var(--text-primary)] md:text-5xl">
          How It Works
        </h1>
        <p className="mt-4 text-center text-[var(--text-secondary)] max-w-lg mx-auto">
          Turn customer activity into a polished social proof experience in four practical steps.
        </p>

        <div className="mt-12 grid gap-8 md:grid-cols-2">
          {STEPS.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.title} className="lt-card flex gap-4 p-6 transition-transform duration-200 hover:-translate-y-1">
                <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-[var(--surface-muted)]">
                  <Icon size={22} strokeWidth={1.5} className="text-[var(--lt-purple)]" />
                </div>
                <div>
                  <p className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Step {index + 1}</p>
                  <h3 className="mt-1 text-lg font-bold text-[var(--text-primary)]">{step.title}</h3>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{step.description}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-12 text-center">
          <Link href="/dashboard" className="lt-btn lt-btn-lg lt-btn-primary">
            Start Free Trial
            <ArrowRight size={16} />
          </Link>
        </div>
      </section>
    </main>
  );
}
