import {
  BriefcaseBusiness,
  Dumbbell,
  Globe,
  Home,
  MonitorSmartphone,
  PawPrint,
  ShieldCheck,
  Sparkles,
  Utensils,
  WalletCards,
} from "lucide-react";

type CategoryArtworkProps = {
  id: string;
  className?: string;
};

const ART_STYLES: Record<
  string,
  {
    gradient: string;
    icon: React.ComponentType<{ className?: string }>;
    accent: string;
    stroke: string;
  }
> = {
  electronics: {
    gradient: "from-violet-100 via-fuchsia-50 to-orange-50",
    icon: MonitorSmartphone,
    accent: "bg-violet-500/12 text-violet-700",
    stroke: "text-violet-700/35",
  },
  hosting: {
    gradient: "from-cyan-100 via-sky-50 to-violet-50",
    icon: Globe,
    accent: "bg-cyan-500/12 text-cyan-700",
    stroke: "text-cyan-700/35",
  },
  saas: {
    gradient: "from-emerald-100 via-teal-50 to-cyan-50",
    icon: BriefcaseBusiness,
    accent: "bg-emerald-500/12 text-emerald-700",
    stroke: "text-emerald-700/35",
  },
  beauty: {
    gradient: "from-rose-100 via-pink-50 to-orange-50",
    icon: Sparkles,
    accent: "bg-rose-500/12 text-rose-700",
    stroke: "text-rose-700/35",
  },
  "pet-care": {
    gradient: "from-amber-100 via-orange-50 to-rose-50",
    icon: PawPrint,
    accent: "bg-amber-500/12 text-amber-700",
    stroke: "text-amber-700/35",
  },
  home: {
    gradient: "from-slate-100 via-violet-50 to-rose-50",
    icon: Home,
    accent: "bg-slate-500/12 text-slate-700",
    stroke: "text-slate-700/35",
  },
  kitchen: {
    gradient: "from-orange-100 via-amber-50 to-rose-50",
    icon: Utensils,
    accent: "bg-orange-500/12 text-orange-700",
    stroke: "text-orange-700/35",
  },
  fitness: {
    gradient: "from-lime-100 via-emerald-50 to-teal-50",
    icon: Dumbbell,
    accent: "bg-lime-500/12 text-lime-700",
    stroke: "text-lime-700/35",
  },
  travel: {
    gradient: "from-blue-100 via-sky-50 to-cyan-50",
    icon: Globe,
    accent: "bg-blue-500/12 text-blue-700",
    stroke: "text-blue-700/35",
  },
  finance: {
    gradient: "from-emerald-100 via-green-50 to-lime-50",
    icon: WalletCards,
    accent: "bg-emerald-500/12 text-emerald-700",
    stroke: "text-emerald-700/35",
  },
  insurance: {
    gradient: "from-violet-100 via-indigo-50 to-blue-50",
    icon: ShieldCheck,
    accent: "bg-violet-500/12 text-violet-700",
    stroke: "text-violet-700/35",
  },
};

export default function CategoryArtwork({ id, className }: CategoryArtworkProps) {
  const style = ART_STYLES[id] ?? ART_STYLES.electronics;
  const Icon = style.icon;
  const gradientId = `card-${id}-line`;

  return (
    <div className={`relative overflow-hidden rounded-[1.5rem] border border-white/70 bg-gradient-to-br ${style.gradient} ${className ?? ""}`}>
      <div className="absolute inset-0 bg-[linear-gradient(140deg,rgba(255,255,255,0.68),rgba(255,255,255,0.2))]" aria-hidden="true" />
      <div className="relative flex h-full min-h-[168px] items-center justify-between px-6 py-6">
        <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl ${style.accent}`}>
          <Icon className="h-6 w-6" aria-hidden="true" />
        </div>

        <svg viewBox="0 0 220 140" className={`h-[112px] w-[176px] ${style.stroke}`} aria-hidden="true">
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="currentColor" stopOpacity="0.65" />
              <stop offset="100%" stopColor="currentColor" stopOpacity="0.25" />
            </linearGradient>
          </defs>
          <rect x="24" y="22" width="170" height="96" rx="22" fill="none" stroke={`url(#${gradientId})`} strokeWidth="1.8" />
          <rect x="40" y="38" width="92" height="56" rx="15" fill="none" stroke={`url(#${gradientId})`} strokeWidth="1.6" />
          <circle cx="162" cy="50" r="18" fill="none" stroke={`url(#${gradientId})`} strokeWidth="1.6" />
          <circle cx="176" cy="96" r="11" fill="none" stroke={`url(#${gradientId})`} strokeWidth="1.6" />
          <path d="M30 104c16-21 34-32 54-32 26 0 38 14 57 14 16 0 30-6 46-19" stroke={`url(#${gradientId})`} strokeWidth="5.5" strokeLinecap="round" fill="none" />
        </svg>
      </div>
    </div>
  );
}