import { Truck, RotateCcw, ShieldCheck } from "lucide-react";

const SIGNALS = [
  {
    icon: Truck,
    title: "Shipping details",
    description: "Delivery information is shown during checkout.",
  },
  {
    icon: RotateCcw,
    title: "Returns & refunds",
    description: "Review the returns policy before placing an order.",
  },
  {
    icon: ShieldCheck,
    title: "Order updates",
    description: "View payment and fulfillment status from your account.",
  },
];

export default function TrustSection() {
  return (
    <section className="py-12 md:py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 md:gap-8">
          {SIGNALS.map((signal) => {
            const Icon = signal.icon;
            return (
              <div key={signal.title} className="text-center">
                <div className="w-12 h-12 mx-auto rounded-full bg-[var(--surface-muted)] flex items-center justify-center">
                  <Icon size={22} strokeWidth={1.5} className="text-[var(--text-secondary)]" />
                </div>
                <h3 className="mt-3 text-sm font-bold text-[var(--text-primary)]">{signal.title}</h3>
                <p className="mt-1 text-xs text-[var(--text-secondary)]">{signal.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
