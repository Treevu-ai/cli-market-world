"use client";
import { useEffect, useState, useRef } from "react";

const items = [
  { end: 3600, suffix: "+", label: "Retailers VTEX activos en 67 paises" },
  { end: 67, suffix: "", label: "Paises con cobertura real" },
  { end: 12, suffix: "", label: "Lineas de negocio" },
  { end: 12, suffix: "", label: "Herramientas MCP" },
];

function Counter({ end, suffix, label, delay }: { end: number; suffix: string; label: string; delay: number }) {
  const [count, setCount] = useState(0);
  const [visible, setVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setTimeout(() => setVisible(true), delay); }, { threshold: 0.5 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, [delay]);
  useEffect(() => {
    if (!visible) return;
    let start = 0; const dur = 2500;
    const step = (t: number) => { if (!start) start = t; const p = Math.min((t-start)/dur,1); setCount(Math.floor((1-Math.pow(1-p,4))*end)); if (p<1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }, [visible, end]);
  return (
    <div ref={ref} className={`flex flex-col gap-2 transition-all duration-700 ${visible?"opacity-100 translate-y-0":"opacity-0 translate-y-4"}`}>
      <span className="text-4xl lg:text-5xl font-grotesk font-bold text-white tabular-nums">{count.toLocaleString()}{suffix}</span>
      <span className="text-xs font-mono text-white/30 uppercase tracking-wider leading-tight">{label}</span>
    </div>
  );
}

export default function StatsSection() {
  return (
    <section className="relative flex flex-col w-full py-24 px-6 lg:px-12 md:py-[120px] gap-10" style={{background:"linear-gradient(135deg, #0A0A0A 0%, #0D1F17 50%, #0A0A0A 100%)"}}>
      <div className="absolute inset-0 opacity-[0.03]" style={{backgroundImage:"radial-gradient(circle at 70% 30%, #00FF88 0%, transparent 60%)"}}/>
      <div className="relative z-10 flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-[#00FF88]/60"><span className="w-8 h-px bg-[#00FF88]/40"/>Escala</span>
        <h2 className="text-[clamp(2rem,5vw,5rem)] font-grotesk font-bold text-white leading-[0.92] whitespace-pre-line">{"El ecosistema\nVTEX completo."}</h2>
        <p className="text-white/40 font-mono text-sm leading-relaxed">Un conector generico. Una linea de JSON por retailer. Infraestructura invisible.</p>
      </div>
      <div className="relative z-10 flex flex-wrap gap-8 sm:gap-12 lg:gap-20 max-w-[900px]">
        {items.map((s,i)=><Counter key={i} end={s.end} suffix={s.suffix} label={s.label} delay={i*150}/>)}
      </div>
      <div className="relative z-10 max-w-[900px] grid grid-cols-2 sm:grid-cols-4 gap-4">
        {["LATAM","Europa","Norteamerica","Asia-Pacifico"].map(r=><div key={r} className="bg-white/[0.02] border border-white/[0.04] px-4 py-3 text-center font-mono text-[10px] text-white/30 uppercase tracking-widest hover:bg-white/[0.04] transition-colors">{r}</div>)}
      </div>
    </section>
  );
}
