"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { RotateCcw } from "lucide-react";
import { trackSafeEvent } from "@/lib/analytics";
import { calculateBreakEven, validateBreakEvenInputs, type BreakEvenCalculation } from "@/lib/breakEvenCalculator";

const currencyFormatter = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 });
const numberFormatter = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 });
function currency(value: number) { return Number.isFinite(value) ? `₹${currencyFormatter.format(value)}` : "Not available"; }
function number(value: number) { return Number.isFinite(value) ? numberFormatter.format(value) : "Not available"; }

export default function BreakEvenCalculator() {
  const [fixedInput, setFixedInput] = useState("");
  const [variableInput, setVariableInput] = useState("");
  const [sellingInput, setSellingInput] = useState("");
  const fixedCosts = Number(fixedInput);
  const variableCost = Number(variableInput);
  const sellingPrice = Number(sellingInput);
  const error = fixedInput.trim() === "" ? "Fixed costs are required." : variableInput.trim() === "" ? "Variable cost is required." : sellingInput.trim() === "" ? "Selling price is required." : validateBreakEvenInputs(fixedCosts, variableCost, sellingPrice);
  const calculation = useMemo<BreakEvenCalculation | null>(() => { if (error) return null; try { return calculateBreakEven(fixedCosts, variableCost, sellingPrice); } catch { return null; } }, [error, fixedCosts, sellingPrice, variableCost]);
  const completionTracked = useRef(false);
  useEffect(() => {
    if (calculation && !completionTracked.current) {
      trackSafeEvent("tool_complete", { tool_name: "break-even-calculator" });
      completionTracked.current = true;
    }
  }, [calculation]);
  function reset() { setFixedInput(""); setVariableInput(""); setSellingInput(""); }

  return <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(340px,0.85fr)]"><form className="lt-card" onSubmit={(event) => event.preventDefault()} noValidate><div className="flex items-start justify-between gap-4"><div><p className="lt-eyebrow">Inputs</p><h2 className="lt-heading-2 mt-2">Enter your costs</h2></div><button type="button" onClick={reset} className="lt-btn lt-btn-sm lt-btn-ghost shrink-0" aria-label="Reset break-even calculator"><RotateCcw size={15} /> Reset</button></div><div className="mt-8 space-y-6"><MoneyField label="Fixed costs" id="fixed-costs" value={fixedInput} onChange={setFixedInput} help="Costs that do not change with each unit sold." /><MoneyField label="Variable cost per unit" id="variable-cost" value={variableInput} onChange={setVariableInput} help="The cost to produce or deliver one unit." /><MoneyField label="Selling price per unit" id="break-even-selling-price" value={sellingInput} onChange={setSellingInput} help="The price your customer pays for one unit." /></div>{error && <p className="mt-5 text-xs font-semibold text-[var(--lt-accent-dark)]" role="alert">{error}</p>}</form><section className="lt-card" aria-live="polite" aria-label="Break-even calculator results"><p className="lt-eyebrow">Your result</p>{calculation ? <Results calculation={calculation} /> : <div className="flex min-h-64 items-center justify-center py-10 text-center"><p className="max-w-xs text-sm leading-relaxed text-[var(--text-secondary)]">Enter fixed costs, variable cost, and selling price to find your break-even point.</p></div>}</section></div>;
}

function MoneyField({ label, id, value, onChange, help }: { label: string; id: string; value: string; onChange: (value: string) => void; help: string }) { return <div><label htmlFor={id} className="lt-label mb-2 block">{label}</label><div className="flex h-[46px] overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--surface)] focus-within:border-[var(--ring)] focus-within:ring-2 focus-within:ring-[var(--ring)]/20"><span className="flex w-11 shrink-0 items-center justify-center border-r border-[var(--border)] text-sm font-semibold text-[var(--text-muted)]" aria-hidden="true">₹</span><input id={id} className="min-w-0 flex-1 border-0 bg-transparent px-3 py-2 text-[var(--text-primary)] outline-none" type="text" inputMode="decimal" value={value} onChange={(event) => onChange(event.target.value)} placeholder="0.00" /></div><p className="mt-1.5 text-xs text-[var(--text-muted)]">{help}</p></div>; }
function Results({ calculation }: { calculation: BreakEvenCalculation }) { return <div className="mt-6"><div className="border-b border-[var(--border)] pb-6"><p className="text-sm font-semibold text-[var(--text-secondary)]">Break-even units</p><p className="mt-2 break-words text-4xl font-black text-[var(--lt-primary)]">{number(calculation.breakEvenUnits)}</p><p className="mt-2 text-sm text-[var(--text-secondary)]">Sell at least this many whole units.</p></div><div className="mt-6 grid gap-3 sm:grid-cols-2"><Result label="Break-even revenue" value={currency(calculation.breakEvenRevenue)} /><Result label="Contribution per unit" value={currency(calculation.contributionPerUnit)} /></div></div>; }
function Result({ label, value }: { label: string; value: string }) { return <div className="border border-[var(--border)] bg-[var(--surface-soft)] p-4"><p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">{label}</p><p className="mt-2 break-words text-lg font-bold text-[var(--text-primary)]">{value}</p></div>; }
