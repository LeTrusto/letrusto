"use client";

import { useMemo, useState } from "react";
import { RotateCcw } from "lucide-react";
import { calculatePricing, validatePricingInputs, type PricingCalculation } from "@/lib/pricingCalculator";

const currencyFormatter = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 });
const percentFormatter = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 });

function currency(value: number) { return Number.isFinite(value) ? `₹${currencyFormatter.format(value)}` : "Not available"; }
function percent(value: number | null) { return value === null ? "Not available" : `${percentFormatter.format(value)}%`; }

export default function PricingCalculator() {
  const [costInput, setCostInput] = useState("");
  const [marginInput, setMarginInput] = useState("");
  const cost = Number(costInput);
  const margin = Number(marginInput);
  const error = costInput.trim() === "" ? "Cost is required." : marginInput.trim() === "" ? "Profit margin is required." : validatePricingInputs(cost, margin);
  const calculation = useMemo<PricingCalculation | null>(() => {
    if (error) return null;
    try { return calculatePricing(cost, margin); } catch { return null; }
  }, [cost, error, margin]);

  function reset() { setCostInput(""); setMarginInput(""); }

  return <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(340px,0.85fr)]"><form className="lt-card" onSubmit={(event) => event.preventDefault()} noValidate><div className="flex items-start justify-between gap-4"><div><p className="lt-eyebrow">Inputs</p><h2 className="lt-heading-2 mt-2">Set your target</h2></div><button type="button" onClick={reset} className="lt-btn lt-btn-sm lt-btn-ghost shrink-0" aria-label="Reset pricing calculator"><RotateCcw size={15} /> Reset</button></div><div className="mt-8 space-y-6"><MoneyField label="Cost" id="pricing-cost" value={costInput} onChange={setCostInput} help="Your cost for the product or service." /><div><label htmlFor="target-margin" className="lt-label mb-2 block">Desired profit margin</label><div className="relative"><input id="target-margin" className="lt-input pr-9" type="text" inputMode="decimal" value={marginInput} onChange={(event) => setMarginInput(event.target.value)} placeholder="25" aria-invalid={Boolean(error && marginInput)} aria-describedby="target-margin-help" /><span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-sm font-semibold text-[var(--text-muted)]">%</span></div><p id="target-margin-help" className="mt-1.5 text-xs text-[var(--text-muted)]">Enter a margin from 0% up to, but not including, 100%.</p></div></div>{error && <p className="mt-5 text-xs font-semibold text-[var(--lt-accent-dark)]" role="alert">{error}</p>}</form><section className="lt-card" aria-live="polite" aria-label="Pricing calculator results"><p className="lt-eyebrow">Your result</p>{calculation ? <Results calculation={calculation} /> : <div className="flex min-h-64 items-center justify-center py-10 text-center"><p className="max-w-xs text-sm leading-relaxed text-[var(--text-secondary)]">Enter a cost and desired margin to calculate a selling price.</p></div>}</section></div>;
}

function MoneyField({ label, id, value, onChange, help }: { label: string; id: string; value: string; onChange: (value: string) => void; help: string }) { return <div><label htmlFor={id} className="lt-label mb-2 block">{label}</label><div className="relative"><span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm font-semibold text-[var(--text-muted)]" aria-hidden="true">₹</span><input id={id} className="lt-input pl-8" type="text" inputMode="decimal" value={value} onChange={(event) => onChange(event.target.value)} placeholder="0.00" /></div><p className="mt-1.5 text-xs text-[var(--text-muted)]">{help}</p></div>; }

function Results({ calculation }: { calculation: PricingCalculation }) { return <div className="mt-6"><div className="border-b border-[var(--border)] pb-6"><p className="text-sm font-semibold text-[var(--text-secondary)]">Recommended selling price</p><p className="mt-2 break-words text-4xl font-black text-[var(--lt-primary)]">{currency(calculation.sellingPrice)}</p></div><div className="mt-6 grid gap-3 sm:grid-cols-3"><Result label="Estimated profit" value={currency(calculation.profit)} /><Result label="Profit margin" value={percent(calculation.margin)} /><Result label="Markup" value={percent(calculation.markup)} /></div></div>; }
function Result({ label, value }: { label: string; value: string }) { return <div className="border border-[var(--border)] bg-[var(--surface-soft)] p-4"><p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">{label}</p><p className="mt-2 break-words text-lg font-bold text-[var(--text-primary)]">{value}</p></div>; }
