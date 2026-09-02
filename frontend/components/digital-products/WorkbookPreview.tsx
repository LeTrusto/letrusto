import type { DigitalProduct } from "@/types/digital-products";

export default function WorkbookPreview({ product }: { product: DigitalProduct }) {
  const freelancer = product.slug === "freelancer-rate-project-pricing-toolkit";
  return (
    <div className="border border-[#b8cec5] bg-[#e8f1ee] p-4 shadow-[0_16px_35px_-22px_rgba(23,60,50,0.65)] sm:p-6">
      <div className="border border-[#b8cec5] bg-[#f7fbf8] p-4 sm:p-6">
        <div className="flex items-start justify-between gap-4 border-b border-[#c9dcd4] pb-5"><div><p className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#28604e]">{product.previewLabel}</p><h2 className="mt-2 text-xl font-black text-[#173c32] sm:text-2xl">{freelancer ? "Rate & quote planner" : "Monthly finance dashboard"}</h2></div><span className="border border-[#b8cec5] bg-white px-2 py-1 text-[10px] font-bold text-[#28604e]">SHEET 01</span></div>
        {freelancer ? <div className="mt-5 grid gap-3 sm:grid-cols-3"><Metric label="Monthly target" value="₹70,000" /><Metric label="Billable hours" value="64 hrs" /><Metric label="Hourly floor" value="₹1,093.75" /></div> : <div className="mt-5 grid gap-3 sm:grid-cols-3"><Metric label="Revenue" value="₹1,20,000" /><Metric label="Expenses" value="₹68,500" /><Metric label="Operating profit" value="₹51,500" /></div>}
        <div className="mt-5 overflow-x-auto"><table className="w-full min-w-[420px] border-collapse text-left text-xs"><thead><tr className="bg-[#dcece5] text-[#28604e]"><th className="border border-[#b8cec5] px-3 py-2 font-bold">Month</th><th className="border border-[#b8cec5] px-3 py-2 font-bold">Revenue</th><th className="border border-[#b8cec5] px-3 py-2 font-bold">Expenses</th><th className="border border-[#b8cec5] px-3 py-2 font-bold">Margin</th></tr></thead><tbody>{[["April", "₹98,000", "₹61,200", "37.6%"], ["May", "₹1,08,000", "₹64,750", "40.0%"], ["June", "₹1,20,000", "₹68,500", "42.9%"]].map((row) => <tr key={row[0]}>{row.map((cell, index) => <td key={`${row[0]}-${index}`} className="border border-[#c9dcd4] px-3 py-2 text-[#173c32]">{cell}</td>)}</tr>)}</tbody></table></div>
        <p className="mt-4 text-[11px] leading-5 text-[#52766a]">Preview values are examples. The delivered workbook is editable and includes blank input areas for your business.</p>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="border border-[#b8cec5] bg-white p-3"><p className="text-[10px] font-bold uppercase tracking-wide text-[#52766a]">{label}</p><p className="mt-2 text-lg font-black text-[#173c32]">{value}</p></div>;
}