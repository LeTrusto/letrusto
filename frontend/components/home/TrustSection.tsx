import { BadgeCheck, Clock3, Lightbulb } from "lucide-react";

const SIGNALS = [
  {
    icon: Lightbulb,
    title: "Practical first",
    description: "Solutions are shaped around real tasks and useful outcomes.",
  },
  {
    icon: Clock3,
    title: "Built to save time",
    description: "Simple resources and services for work that needs doing.",
  },
  {
    icon: BadgeCheck,
    title: "Clear and transparent",
    description: "What is available, planned or scoped is stated plainly.",
  },
];

export default function TrustSection() {
  return (
    <section className="py-16 md:py-20 bg-[var(--background)]">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 md:gap-8">
          {SIGNALS.map((signal) => {
            const Icon = signal.icon;
            return (
              <div key={signal.title} className="text-center">
                <div className="w-16 h-16 mx-auto rounded-full bg-[var(--lt-primary)]/15 flex items-center justify-center">
                  <Icon size={36} strokeWidth={1.5} className="text-[var(--lt-primary)]" />
                </div>
                <h3 className="mt-4 text-base font-bold text-[var(--text-primary)]">{signal.title}</h3>
                <p className="mt-2 text-sm text-[var(--text-secondary)]">{signal.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
