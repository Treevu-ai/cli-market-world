"use client";
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLang } from "@/lib/LanguageContext";

gsap.registerPlugin(ScrollTrigger);

const labels = ["stats_retailers", "stats_countries", "stats_lines", "stats_tools"];
const ends = [38, 9, 6, 36];
const suffixes = ["+", "", "", ""];

function Counter({ end, suffix, label, delay }: { end: number; suffix: string; label: string; delay: number }) {
  const valRef = useRef<HTMLSpanElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(containerRef.current,
        { opacity: 0, y: 20 },
        {
          opacity: 1, y: 0, duration: 0.8, delay: delay / 1000,
          scrollTrigger: { trigger: containerRef.current, start: "top 85%", toggleActions: "play none none none" },
        }
      );
      gsap.fromTo(valRef.current,
        { textContent: 0 },
        {
          textContent: end, duration: 2.5, delay: (delay + 200) / 1000,
          ease: "power2.out", snap: { textContent: 1 },
          scrollTrigger: { trigger: containerRef.current, start: "top 85%", toggleActions: "play none none none" },
        }
      );
    }, containerRef);
    return () => ctx.revert();
  }, [end, delay]);

  return (
    <div ref={containerRef} className="flex flex-col gap-2">
      <span className="text-4xl lg:text-5xl font-grotesk font-bold text-white tabular-nums">
        <span ref={valRef}>0</span>{suffix}
      </span>
      <span className="text-xs font-mono text-white/30 uppercase tracking-wider leading-tight">{label}</span>
    </div>
  );
}

export default function StatsSection() {
  const { t: _t } = useLang();
  const gridRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const items = gridRef.current?.querySelectorAll(".region-item");
      if (items) {
        gsap.fromTo(items, { opacity: 0, y: 8 }, {
          opacity: 1, y: 0, duration: 0.5, stagger: 0.08,
          scrollTrigger: { trigger: gridRef.current, start: "top 90%", toggleActions: "play none none none" },
        });
      }
    }, gridRef);
    return () => ctx.revert();
  }, []);

  return (
    <section id="stats" className="relative flex flex-col w-full py-24 px-6 lg:px-12 md:py-[120px] gap-10" style={{ background: "linear-gradient(135deg, #131313 0%, #0d0d20 50%, #131313 100%)" }}>
      <div className="absolute inset-0 opacity-[0.03] parallax-glow" style={{ backgroundImage: "radial-gradient(circle at 70% 30%, #3cffd0 0%, transparent 60%)" }} />
      <div className="relative z-10 flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-[#3cffd0]/60"><span className="w-8 h-px bg-[#3cffd0]/40" />{_t("stats_label")}</span>
        <h2 className="text-[clamp(2rem,5vw,5rem)] font-grotesk font-bold text-white leading-[0.92] whitespace-pre-line">{_t("stats_title")}</h2>
        <p className="text-white/40 font-mono text-sm leading-relaxed">{_t("stats_sub")}</p>
      </div>
      <div className="relative z-10 flex flex-wrap gap-8 sm:gap-12 lg:gap-20 max-w-[900px]">
        {labels.map((lk, i) => <Counter key={i} end={ends[i]} suffix={suffixes[i]} label={_t(lk)} delay={i * 150} />)}
      </div>
      <div ref={gridRef} className="relative z-10 max-w-[900px] grid grid-cols-2 sm:grid-cols-4 gap-4">
        {["LATAM", "Europa", "Norteamérica", "Asia-Pacífico"].map((r, i) => (
          <div key={r} className="region-item bg-white/[0.02] border border-white/[0.04] px-4 py-3 text-center font-mono text-[10px] text-white/30 uppercase tracking-widest hover:bg-white/[0.04] transition-colors">{r}</div>
        ))}
      </div>
    </section>
  );
}
