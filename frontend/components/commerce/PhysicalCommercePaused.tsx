import Link from "next/link";

export default function PhysicalCommercePaused({ area }: { area: string }) {
  return (
    <main className="mx-auto flex min-h-[60vh] max-w-2xl items-center justify-center px-4 py-20 text-center">
      <div>
        <p className="mb-4 text-sm font-bold uppercase tracking-[0.2em] text-[var(--lt-accent)]">LeTrusto</p>
        <h1 className="lt-heading-1">{area} is currently paused</h1>
        <p className="mt-4 text-[var(--text-secondary)]">
          LeTrusto is focused on social proof and review tools for businesses. Physical commerce is not available.
        </p>
        <Link href="/" className="lt-btn lt-btn-primary mt-7 inline-flex">Return home</Link>
      </div>
    </main>
  );
}
