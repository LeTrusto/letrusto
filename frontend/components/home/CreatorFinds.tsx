import { Users } from "lucide-react";

export default function CreatorFinds() {
  return (
    <section className="bg-[var(--background)] py-14 md:py-20">
      <div className="max-w-7xl mx-auto px-4 md:px-6 text-center">
        <div className="w-16 h-16 mx-auto rounded-full bg-[var(--lt-primary)]/15 flex items-center justify-center">
          <Users size={36} strokeWidth={1.5} className="text-[var(--lt-primary)]" />
        </div>
        <h2 className="mt-6 text-3xl md:text-4xl font-bold text-[var(--text-primary)]">Creator Finds</h2>
        <p className="mt-3 text-[var(--text-secondary)] font-medium max-w-md mx-auto">
          Hand-picked products by creators we trust. Coming soon.
        </p>
      </div>
    </section>
  );
}
