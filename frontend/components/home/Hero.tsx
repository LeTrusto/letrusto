export default function Hero() {
  return (
    <section className="bg-[var(--background)] py-16 md:py-20 lg:py-24">
      <div className="max-w-[1280px] mx-auto px-4 md:px-6 text-center">
        <div className="mb-7 inline-block">
          <span className="text-base font-black tracking-[0.22em] text-[var(--lt-accent)] uppercase sm:text-lg">BUILD WITH CONFIDENCE</span>
        </div>
        <h1 className="mb-6 text-5xl font-black leading-[1.08] tracking-tight text-[var(--text-primary)] sm:text-6xl md:text-6xl lg:text-7xl">
          TOOLS FOR<br />
          YOUR NEXT MOVE.
        </h1>
        <p className="mx-auto mt-6 max-w-[680px] text-lg font-medium leading-relaxed text-[var(--text-secondary)]">
          LeTrusto is moving toward practical digital tools, templates and services for Indian businesses.
        </p>
      </div>
    </section>
  );
}
