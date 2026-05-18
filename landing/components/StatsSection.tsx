"use client";
import { useEffect, useState, useRef } from "react";

function AnimatedNumber({ end, suffix }: { end: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const [done, setDone] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting && !done) { setDone(true); let start=0; const dur=2000; const step=(t:number)=>{if(!start) start=t; const p=Math.min((t-start)/dur,1); setCount(Math.floor((1-Math.pow(1-p,3))*end)); if(p<1) requestAnimationFrame(step);}; requestAnimationFrame(step); }
    }, { threshold: 0.5 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, [end, done]);
  return <span ref={ref} className="text-4xl lg:text-5xl font-grotesk font-bold text-white tabular-nums">{count.toLocaleString()}{suffix||""}</span>;
}

export default function StatsSection() {
  return (
    <section className="relative flex flex-col w-full bg-[#060606] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#FFD600]/40"/>Impacto</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05]">El ecosistema VTEX completo.</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">Cifras reales. Un conector. Cero interfaces.</p>
      </div>
      <div className="flex flex-wrap gap-8 sm:gap-12 lg:gap-20 max-w-[900px]">
        <div className="flex flex-col gap-2"><AnimatedNumber end={3600} suffix="+" /><span className="text-xs font-mono text-white/30 uppercase tracking-wider">Retailers VTEX</span></div>
        <div className="flex flex-col gap-2"><AnimatedNumber end={67} /><span className="text-xs font-mono text-white/30 uppercase tracking-wider">Países</span></div>
        <div className="flex flex-col gap-2"><AnimatedNumber end={12} /><span className="text-xs font-mono text-white/30 uppercase tracking-wider">Líneas de negocio</span></div>
        <div className="flex flex-col gap-2"><AnimatedNumber end={12} /><span className="text-xs font-mono text-white/30 uppercase tracking-wider">Herramientas MCP</span></div>
      </div>
      <p className="text-white/15 font-mono text-[10px] uppercase tracking-widest max-w-[600px]">UN CONECTOR GENERICO · UNA LINEA DE JSON POR RETAILER · INFRAESTRUCTURA INVISIBLE</p>
    </section>
  );
}
