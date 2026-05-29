"use client";
import { useEffect, useRef } from "react";
import { motion, useInView, useSpring, useTransform } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const stats = [
  { end: MARKET_STATS.retailersDefined, label: "retailers" },
  { end: MARKET_STATS.countries, label: "países" },
  { end: MARKET_STATS.platforms, label: "platforms" },
  { end: MARKET_STATS.mcpTools, label: "MCP tools" },
];

function Counter({ end, label, delay }: { end: number; label: string; delay: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "0px 0px -120px 0px" });
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
      <motion.span ref={ref} className="text-[28px] font-medium text-[var(--wise-ink)] tracking-tight tabular-nums">{display}</motion.span>
      <span className="text-xs text-[var(--wise-body)] font-mono uppercase tracking-widest">{label}</span>
    </div>
  );
}

export default function StatsSection() {
  const { t: _t, lang } = useLang();
  const isES = lang === "es";
  const labels_es: Record<string, string> = {
    retailers: "retailers definidos",
    países: "países",
    platforms: "plataformas",
    "MCP tools": "herramientas MCP",
  };
  const labels_en: Record<string, string> = {
    retailers: "retailers defined",
    países: "countries",
    platforms: "platforms",
    "MCP tools": "MCP tools",
  };
  const dict: Record<string, string> = isES ? labels_es : labels_en;

  return (
    <section id="stats" className="relative bg-[var(--wise-canvas-soft)] py-24 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[var(--wise-body)] font-mono uppercase tracking-[0.15em] mb-8">{_t("stats_label")}</p>
        <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-3 tracking-tight whitespace-pre-line">{_t("stats_title")}</h2>
        <p className="text-sm text-[var(--wise-body)] max-w-md mx-auto mb-4">{_t("stats_sub")}</p>
        <p className="text-xs text-[var(--wise-mute)] font-mono mb-12">
          {isES ? MARKET_STATS.retailersPhraseEs : MARKET_STATS.retailersPhraseEn}
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-8">
          {stats.map((s, i) => (<Counter key={s.label} end={s.end} label={dict[s.label] || s.label} delay={i * 150} />))}
        </div>
      </div>
    </section>
  );
}
