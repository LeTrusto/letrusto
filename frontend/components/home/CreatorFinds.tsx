import { Users } from "lucide-react";

export default function CreatorFinds() {
  return (
    <section className="py-12 md:py-16">
      <div className="max-w-7xl mx-auto px-4 md:px-6 text-center">
        <div className="w-12 h-12 mx-auto rounded-full bg-[var(--surface-muted)] flex items-center justify-center">
          <Users size={22} strokeWidth={1.5} className="text-[var(--text-secondary)]" />
        </div>
        <h2 className="mt-4 lt-heading-2">Creator Finds</h2>
        <p className="mt-2 text-sm text-[var(--text-secondary)] max-w-md mx-auto">
          Hand-picked products by creators we trust. Coming soon.
        </p>
      </div>
    </section>
  );
}
