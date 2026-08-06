"use client";

import { Loader2, MailCheck } from "lucide-react";
import { useState, useTransition } from "react";

import { buildApiUrl, IS_API_CONFIGURED } from "@/services/api";

type HomeNewsletterSectionProps = {
  title: string;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
};

export default function HomeNewsletterSection({
  title,
  subtitle,
}: HomeNewsletterSectionProps) {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isPending || !email.trim()) {
      return;
    }

    setError(null);
    setMessage(null);

    startTransition(async () => {
      try {
        if (IS_API_CONFIGURED) {
          const response = await fetch(buildApiUrl("/support/tickets"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: email.trim(),
              category: "feedback",
              subject: "Newsletter signup",
              body: "Please add me to LeTrusto product updates and launch notes.",
            }),
          });

          if (!response.ok) {
            throw new Error("We could not save your subscription right now.");
          }
        } else {
          window.localStorage.setItem("letrusto:newsletter-interest", email.trim());
        }

        setMessage("You’re on the list for launch notes and future buying updates.");
        setEmail("");
      } catch {
        setError("Unable to save your email right now. Please try again shortly.");
      }
    });
  }

  return (
    <section className="mx-auto mt-20 w-full max-w-7xl px-6 pb-20">
      <div className="overflow-hidden rounded-[2rem] border border-slate-200 bg-[radial-gradient(circle_at_top_left,_rgba(125,211,252,0.18),_transparent_36%),radial-gradient(circle_at_bottom_right,_rgba(15,23,42,0.06),_transparent_42%),white] p-8 shadow-sm md:p-10">
        <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">Stay connected</p>
            <h2 className="mt-3 text-3xl font-black tracking-tight text-slate-950 md:text-5xl">{title}</h2>
            {subtitle ? <p className="mt-4 max-w-2xl text-base text-slate-600 md:text-lg">{subtitle}</p> : null}
            <div className="mt-6 flex flex-wrap gap-2 text-sm text-slate-500">
              <span className="rounded-full bg-white px-3 py-1 shadow-sm">Product updates</span>
              <span className="rounded-full bg-white px-3 py-1 shadow-sm">New guides</span>
              <span className="rounded-full bg-white px-3 py-1 shadow-sm">Category launches</span>
            </div>
          </div>

          <form onSubmit={(event) => { void handleSubmit(event); }} className="rounded-[1.5rem] border border-white/80 bg-white/90 p-5 shadow-lg shadow-slate-200/60">
            <label htmlFor="newsletter-email" className="text-sm font-semibold text-slate-700">
              Email address
            </label>
            <input
              id="newsletter-email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="hello@company.com"
              className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3.5 text-sm text-slate-900 outline-none transition focus:border-sky-300 focus:bg-white focus:ring-4 focus:ring-sky-100"
            />
            <button
              type="submit"
              disabled={isPending}
              className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-950 px-5 py-3.5 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <MailCheck className="h-4 w-4" />}
              {isPending ? "Joining list..." : "Join updates"}
            </button>
            {message ? <p className="mt-3 text-sm text-emerald-700">{message}</p> : null}
            {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
            <p className="mt-3 text-xs leading-relaxed text-slate-500">
              Occasional updates only. No noise, and you can unsubscribe anytime by replying to any update.
            </p>
          </form>
        </div>
      </div>
    </section>
  );
}