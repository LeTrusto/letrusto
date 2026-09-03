"use client";

import { useEffect, useRef, useState } from "react";
import { RotateCcw } from "lucide-react";
import { trackSafeEvent } from "@/lib/analytics";
import { calculateDiscount, validateDiscountInputs } from "@/lib/discountCalculator";

const format = (value: number) => `₹${new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(value)}`;

export default function DiscountCalculator() {
  const [price, setPrice] = useState("");
  const [rate, setRate] = useState("");
  const parsedPrice = Number(price);
  const parsedRate = Number(rate);
  const error = price.trim() === "" ? "Original price is required." : rate.trim() === "" ? "Discount is required." : validateDiscountInputs(parsedPrice, parsedRate);
  const result = error ? null : calculateDiscount(parsedPrice, parsedRate);
  const completionTracked = useRef(false);
  useEffect(() => { if (result && !completionTracked.current) { trackSafeEvent("tool_complete", { tool_name: "discount-calculator" }); completionTracked.current = true; } }, [result]);
  return <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(340px,0.85fr)]"><form className="lt-card" onSubmit={(event) => event.preventDefault()} noValidate><div className="flex items-start justify-between gap-4"><div><p className="lt-eyebrow">Inputs</p><h2 className="lt-heading-2 mt-2">Apply a discount</h2></div><button type="button" onClick={() => { setPrice(""); setRate(""); }} className="lt-btn lt-btn-sm lt-btn-ghost shrink-0" aria-label="Reset discount calculator"><RotateCcw size={15} /> Reset</button></div><div className="mt-8 space-y-6"><Field id="discount-price" label="Original price" value={price} onChange={setPrice} placeholder="799" help="Enter the original price in INR." /><Field id="discount-rate" label="Discount" value={rate} onChange={setRate} placeholder="15" suffix="%" help="Enter a discount from 0% to 100%." /></div>{error && <p className="mt-5 text-xs font-semibold text-[var(--lt-accent-dark)]" role="alert">{error}</p>}</form><section className="lt-card" aria-live="polite" aria-label="Discount calculator results"><p className="lt-eyebrow">Your result</p>{result ? <div className="mt-6 grid gap-3 sm:grid-cols-2"><Result label="You save" value={format(result.savings)} /><Result label="Final price" value={format(result.finalPrice)} /></div> : <div className="flex min-h-64 items-center justify-center py-10 text-center"><p className="max-w-xs text-sm leading-relaxed text-[var(--text-secondary)]">Enter an original price and discount to see the final price.</p></div>}</section></div>;
}

function Field({ id, label, value, onChange, placeholder, suffix, help }: { id: string; label: string; value: string; onChange: (value: string) => void; placeholder: string; suffix?: string; help: string }) { return <div><label htmlFor={id} className="lt-label mb-2 block">{label}</label><div className="flex h-[46px] overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--surface)] focus-within:border-[var(--ring)] focus-within:ring-2 focus-within:ring-[var(--ring)]/20"><input id={id} className="min-w-0 flex-1 border-0 bg-transparent px-3 py-2 text-[var(--text-primary)] outline-none" type="text" inputMode="decimal" value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} aria-describedby={`${id}-help`} />{suffix ? <span className="flex w-11 shrink-0 items-center justify-center border-l border-[var(--border)] text-sm font-semibold text-[var(--text-muted)]" aria-hidden="true">{suffix}</span> : <span className="flex w-11 shrink-0 items-center justify-center border-r border-[var(--border)] text-sm font-semibold text-[var(--text-muted)]" aria-hidden="true">₹</span>}</div><p id={`${id}-help`} className="mt-1.5 text-xs text-[var(--text-muted)]">{help}</p></div>; }
function Result({ label, value }: { label: string; value: string }) { return <div className="border border-[var(--border)] bg-[var(--surface-soft)] p-4"><p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">{label}</p><p className="mt-2 break-words text-xl font-bold text-[var(--text-primary)]">{value}</p></div>; }
