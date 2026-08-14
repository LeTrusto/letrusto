"use client";

import { useState } from "react";
import { Send } from "lucide-react";

export default function NewsletterSignup() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (email.trim()) {
      // Placeholder — no real subscription in Phase 1
      setSubmitted(true);
    }
  }

  return (
    <section className="py-12 md:py-16 bg-[var(--surface-muted)]">
      <div className="max-w-xl mx-auto px-4 md:px-6 text-center">
        <h2 className="lt-heading-2">Stay in the Loop</h2>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">
          Get first access to new drops, exclusive offers, and trending finds. No spam.
        </p>
        {submitted ? (
          <p className="mt-6 text-sm font-semibold text-[var(--lt-success)]">
            Thanks! We&apos;ll keep you posted.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="mt-6 flex gap-2 max-w-sm mx-auto">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="lt-input flex-1"
            />
            <button type="submit" className="lt-btn lt-btn-md lt-btn-primary" aria-label="Subscribe">
              <Send size={16} />
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
