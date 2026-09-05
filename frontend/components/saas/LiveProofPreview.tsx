"use client";

import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, MapPin, Star } from "lucide-react";
import { useEffect, useState } from "react";

const proofItems = [
  { name: "Aarav Mehta", location: "Mumbai", action: "just booked a strategy call", color: "#f97316" },
  { name: "Mira Shah", location: "Bengaluru", action: "started a free trial", color: "#0f766e" },
  { name: "Rohan Kapoor", location: "New Delhi", action: "left a 5-star review", color: "#e11d48" },
];

export default function LiveProofPreview({ color = "#f97316", compact = false }: { color?: string; compact?: boolean }) {
  const [active, setActive] = useState(0);
  useEffect(() => {
    const timer = window.setInterval(() => setActive((value) => (value + 1) % proofItems.length), 3200);
    return () => window.clearInterval(timer);
  }, []);

  const item = proofItems[active];
  return (
    <div className={`relative overflow-hidden border border-[#cad7d2] bg-[#f7faf8] ${compact ? "min-h-[210px]" : "min-h-[390px]"}`}>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_20%,rgba(249,115,22,0.18),transparent_24%),linear-gradient(135deg,#f7faf8_0%,#e5f0eb_100%)]" />
      <div className="absolute left-5 top-5 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.2em] text-[#527267]">
        <span className="h-2 w-2 animate-pulse rounded-full bg-[#e11d48]" /> Live preview
      </div>
      <div className="relative flex h-full min-h-[inherit] items-center justify-center p-5">
        <AnimatePresence mode="wait">
          <motion.div
            key={item.name}
            initial={{ opacity: 0, y: 18, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -14, scale: 0.98 }}
            transition={{ duration: 0.35 }}
            className="w-full max-w-[320px] border border-[#d8e2de] bg-white p-4 shadow-[0_18px_55px_rgba(35,65,54,0.15)]"
            style={{ borderLeft: `4px solid ${color}` }}
          >
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-black text-white" style={{ backgroundColor: item.color }}>
                {item.name.split(" ").map((part) => part[0]).join("")}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1 text-sm font-bold text-[#17382e]">
                  {item.name} <CheckCircle2 className="h-3.5 w-3.5 text-[#0f766e]" />
                </div>
                <div className="mt-1 flex items-center gap-1 text-xs text-[#71877f]"><MapPin className="h-3 w-3" /> {item.location}</div>
                <p className="mt-2 text-sm leading-5 text-[#39564c]">{item.action}</p>
                <div className="mt-2 flex items-center gap-1 text-xs font-bold" style={{ color }}><Star className="h-3.5 w-3.5 fill-current" /> Trusted by real customers</div>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
