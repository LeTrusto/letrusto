import Link from "next/link";
import { ShieldCheck } from "lucide-react";

type Props = {
  compact?: boolean;
  footer?: boolean;
  tone?: "light" | "dark";
};

export default function BrandMark({ compact = false, footer = false, tone = "dark" }: Props) {
  const isLight = tone === "light" || footer;

  return (
    <Link
      href="/"
      aria-label="LeTrusto home"
      className={`inline-flex shrink-0 items-center gap-3 ${isLight ? "text-white" : "text-slate-900"}`}
    >
      <span className={`flex items-center justify-center rounded-xl bg-[#2563eb] text-white shadow-[0_0_24px_rgba(37,99,235,0.35)] ${compact ? "h-9 w-9" : "h-10 w-10"}`}>
        <ShieldCheck size={compact ? 21 : 23} strokeWidth={2.2} />
      </span>
      <span className="flex flex-col leading-none">
        <span className="text-base font-black tracking-tight">LeTrusto</span>
        {!compact && <span className={`mt-1 text-[10px] font-semibold tracking-[0.16em] ${isLight ? "text-slate-400" : "text-slate-500"}`}>Social Proof, Made Visible</span>}
      </span>
    </Link>
  );
}
