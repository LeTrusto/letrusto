import Link from "next/link";
import { ShieldCheck } from "lucide-react";

type Props = {
  compact?: boolean;
  footer?: boolean;
};

export default function BrandMark({ compact = false, footer = false }: Props) {
  return (
    <Link
      href="/"
      aria-label="LeTrusto home"
      className={`inline-flex shrink-0 items-center gap-3 ${footer ? "text-white" : "text-white"}`}
    >
      <span className={`flex items-center justify-center rounded-xl bg-[#2563eb] text-white shadow-[0_0_24px_rgba(37,99,235,0.35)] ${compact ? "h-9 w-9" : "h-10 w-10"}`}>
        <ShieldCheck size={compact ? 21 : 23} strokeWidth={2.2} />
      </span>
      <span className="flex flex-col leading-none">
        <span className="text-base font-black tracking-tight">LeTrusto</span>
        {!compact && <span className="mt-1 text-[10px] font-semibold tracking-[0.16em] text-[#94a3b8]">Social Proof, Made Visible</span>}
      </span>
    </Link>
  );
}
