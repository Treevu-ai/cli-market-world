"use client";
import { useEffect, useRef } from "react";
import { motion, useSpring, useTransform, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";

const labels = ["stats_retailers", "stats_countries", "stats_lines", "stats_tools"];
const ends = [30, 8, 6, 30];
const suffixes = ["+", "", "", ""];

function SpringCounter({ end, suffix, label, delay }: { end: number; suffix: string; label: string; delay: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const spring = useSpring(0, { stiffness: 60, damping: 15, mass: 0.8 });
  const display = useTransform(spring, (v) => Math.floor(v).toLocaleString());

  useEffect(() => {
    if (inView) {
      const timer = setTimeout(() => spring.set(end), delay);
      return () => clearTimeout(timer);
    }
  }, [inView, end, delay, spring]);

  return (
    <div ref={ref} className="flex flex-col gap-2">
      <motion.span
        className="text-4xl lg:text-5xl font-grotesk font-bold text-white tabular-nums"
        initial={{ opacity: 0, y: 12 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6, delay: delay / 1000 }}
      >
        <motion.span>{display}</motion.span>{suffix}
      </motion.span>
      <span className="text-xs font-mono text-white/30 uppercase tracking-wider leading-tight">{label}</span>
    </div>
  );
}

export default function StatsSection() {
  const { t: _t } = useLang();
  return (
    <section className="relative flex flex-col w-full py-24 px-6 lg:px-12 md:py-[120px] gap-10" style={{ background: "linear-gradient(135deg, #131313 0%, #0d0d20 50%, #131313 100%)" }}>
      <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "radial-gradient(circle at 70% 30%, #3cffd0 0%, transparent 60%)" }} />
      <div className="relative z-10 flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-[#3cffd0]/60"><span className="w-8 h-px bg-[#3cffd0]/40" />{_t("stats_label")}</span>
        <h2 className="text-[clamp(2rem,5vw,5rem)] font-grotesk font-bold text-white leading-[0.92] whitespace-pre-line">{_t("stats_title")}</h2>
        <p className="text-white/40 font-mono text-sm leading-relaxed">{_t("stats_sub")}</p>
      </div>
      <div className="relative z-10 flex flex-wrap gap-8 sm:gap-12 lg:gap-20 max-w-[900px]">
        {labels.map((lk, i) => <SpringCounter key={i} end={ends[i]} suffix={suffixes[i]} label={_t(lk)} delay={i * 150} />)}
      </div>
      <div className="relative z-10 max-w-[900px] grid grid-cols-2 sm:grid-cols-4 gap-4">
        {["LATAM", "Europa", "Norteamérica", "Asia-Pacífico"].map(r => <div key={r} className="bg-white/[0.02] border border-white/[0.04] px-4 py-3 text-center font-mono text-[10px] text-white/30 uppercase tracking-widest hover:bg-white/[0.04] transition-colors">{r}</div>)}
      </div>
    </section>
  );
}
