"use client";

import { useEffect, useRef, useState } from "react";
import { RotateCcw } from "lucide-react";
import { trackSafeEvent } from "@/lib/analytics";
import { calculateCommission, validateCommissionInputs } from "@/lib/commissionCalculator";

const format = (value: number) => `₹${new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(value)}`;

export default function CommissionCalculator() {
  const [amount, setAmount] = useState("");
  const [rate, setRate] = useState("");
  const parsedAmount = Number(amount);
  const parsedRate = Number(rate);
  const error = amount.trim() === "" ? "Amount is required." : rate.trim() === "" ? "Commission rate is required." : validateCommissionInputs(parsedAmount, parsedRate);
  const result = error ? null : calculateCommission(parsedAmount, parsedRate);
  const completionTracked = useRef(false);
  useEffect(() => { if (result && !completionTracked.current) { trackSafeEvent("tool_complete", { tool_name: "commission-calculator" }); completionTracked.current = true; } }, [result]);
  return <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(340px,0.85fr)]"><form className="lt-card" onSubmit={(event) => event.preventDefault()} noValidate><div className="flex items-start justify-between gap-4"><div><p className="lt-eyebrow">Inputs</p><h2 className="lt-heading-2 mt-2">Check the split</h2></div><button type="button" onClick={() => { setAmount(""); setRate(""); }} className="lt-btn lt-btn-sm lt-btn-ghost shrink-0" aria-label="Reset commission calculator"><RotateCcw size={15} /> Reset</button></div><div className="mt-8 space-y-6"><Field id="commission-amount" label="Sale or invoice amount" value={amount} onChange={setAmount} placeholder="10000" help="Enter the gross amount in INR." /><Field id="commission-rate" label="Commission rate" value={rate} onChange={setRate} placeholder="12.5" suffix="%" help="Enter a rate from 0% to 100%." /></div>{error && <p className="mt-5 text-xs font-semibold text-[var(--lt-accent-dark)]" role="alert">{error}</p>}</form><section className="lt-card" aria-live="polite" aria-label="Commission calculator results"><p className="lt-eyebrow">Your result</p>{result ? <div className="mt-6 grid gap-3 sm:grid-cols-2"><Result label="Commission" value={format(result.commission)} /><Result label="Amount after commission" value={format(result.netAmount)} /></div> : <div className="flex min-h-64 items-center justify-center py-10 text-center"><p className="max-w-xs text-sm leading-relaxed text-[var(--text-secondary)]">Enter an amount and rate to see the commission split.</p></div>}</section></div>;
}

function Field({ id, label, value, onChange, placeholder, suffix, help }: { id: string; label: string; value: string; onChange: (value: string) => void; placeholder: string; suffix?: string; help: string }) { return <div><label htmlFor={id} className="lt-label mb-2 block">{label}</label><div className="relative"><input id={id} className={`lt-input ${suffix ? "pr-9" : "pl-8"}`} type="text" inputMode="decimal" value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} aria-describedby={`${id}-help`} /><span className={`pointer-events-none absolute ${suffix ? "right-3" : "left-3"} top-1/2 -translate-y-1/2 text-sm font-semibold text-[var(--text-muted)]`} aria-hidden="true">{suffix ?? "₹"}</span></div><p id={`${id}-help`} className="mt-1.5 text-xs text-[var(--text-muted)]">{help}</p></div>; }
function Result({ label, value }: { label: string; value: string }) { return <div className="border border-[var(--border)] bg-[var(--surface-soft)] p-4"><p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">{label}</p><p className="mt-2 break-words text-xl font-bold text-[var(--text-primary)]">{value}</p></div>; }
