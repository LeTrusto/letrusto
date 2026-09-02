import Link from "next/link";

export default function NewsletterSignup() {
  return (
    <section className="py-16 md:py-20 bg-[var(--background)]">
      <div className="max-w-xl mx-auto px-4 md:px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-[var(--text-primary)] mb-2">Something useful is on the way</h2>
        <p className="text-[var(--text-secondary)] font-medium">
          We are preparing digital tools, templates and services for the next chapter of LeTrusto.
        </p>
        <Link href="/support" className="lt-btn lt-btn-lg lt-btn-secondary mt-8 inline-flex">
          Contact LeTrusto
        </Link>
      </div>
    </section>
  );
}
