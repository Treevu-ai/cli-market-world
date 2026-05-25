"use client";
import { useEffect, useRef } from "react";
import { motion, useInView, useSpring, useTransform } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";

const stats = [
  { end: 60, label: "retailers" },
  { end: 11, label: "países" },
  { end: 6, label: "líneas" },
  { end: 36, label: "MCP tools" },
];

function Counter({ end, label, delay }: { end: number; label: string; delay: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const spring = useSpring(0, { stiffness: 60, damping: 20, duration: 2000 });
  const display = useTransform(spring, (v) => Math.round(v).toLocaleString());

  useEffect(() => {
    if (inView) {
      const timer = setTimeout(() => spring.set(end), delay);
      return () => clearTimeout(timer);
    }
  }, [inView, end, delay, spring]);

  return (
    <div className="flex flex-col items-center gap-1">
      <motion.span ref={ref} className="text-[28px] font-medium text-black tracking-tight tabular-nums">{display}</motion.span>
      <span className="text-xs text-[#a3a3a3] font-mono uppercase tracking-widest">{label}</span>
    </div>
  );
}

export default function StatsSection() {
  const { t: _t } = useLang();

  return (
    <section id="stats" className="relative bg-white py-20 border-t border-[#e5e5e5]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#a3a3a3] font-mono uppercase tracking-[0.15em] mb-8">{_t("stats_label")}</p>
        <h2 className="text-[24px] font-medium text-black mb-3 tracking-tight">{_t("stats_title")}</h2>
        <p className="text-sm text-[#737373] max-w-md mx-auto mb-12">{_t("stats_sub")}</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-8">
          {stats.map((s, i) => (<Counter key={s.label} end={s.end} label={s.label} delay={i * 150} />))}
        </div>
      </div>
    </section>
  );
}
