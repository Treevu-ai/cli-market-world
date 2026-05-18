"use client";

import { useEffect, useState } from "react";
import GlitchText from "@/components/GlitchText";

export default function Hero() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <section id="hero" className="relative min-h-screen flex flex-col justify-center px-6 md:px-28 pt-20 pb-24 md:pt-32 md:pb-32 overflow-hidden">
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{
        backgroundImage: "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
        backgroundSize: "64px 64px",
      }} />
      <div className="hidden md:block absolute left-6 top-1/2 -translate-y-1/2">
        <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#444] -rotate-90 origin-left block whitespace-nowrap">
          CLI MARKET
        </span>
      </div>
      <div className="flex-1 flex flex-col justify-center max-w-[900px] w-full">
        <div className="font-grotesk text-[clamp(48px,12vw,120px)] font-bold text-[#F5F5F0] tracking-[-2px] leading-[0.9]">
          {mounted ? <GlitchText text="CLI MARKET" speed={60} delay={200} /> : "CLI MARKET"}
        </div>
        <h2 className="font-mono text-[#666] text-[clamp(12px,2vw,18px)] mt-4 md:mt-6 tracking-[0.15em] uppercase">
          Infraestructura de comercio para agentes de inteligencia artificial
        </h2>
        <p className="mt-8 md:mt-12 max-w-lg font-mono text-[13px] md:text-[14px] text-[#888] leading-relaxed">
          100 retailers en 12 países comparten la misma API VTEX. 
          Construimos la capa de datos que ningún retailer puede construir solo — 
          porque requeriría compartir sus precios con la competencia.
        </p>
        <div className="mt-8 md:mt-12 flex flex-wrap gap-3">
          {[
            { label: "Developers", sub: "CLI · REST · JSON · MCP", color: "#00FF88" },
            { label: "Business", sub: "Data Feed · CIaaS · Analytics", color: "#FFD600" },
            { label: "AI Agents", sub: "12 MCP Tools · Autonomous", color: "#FF6B35" },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2 px-4 py-2 bg-transparent border border-[#222]">
              <div className="w-[5px] h-[5px] rounded-full shrink-0" style={{ backgroundColor: item.color }} />
              <div className="flex flex-col">
                <span className="font-mono text-[10px] font-bold tracking-[1px]" style={{ color: item.color }}>{item.label}</span>
                <span className="font-mono text-[9px] text-[#555]">{item.sub}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-10 md:mt-16 flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-8">
          <a href="https://github.com/Treevu-ai/cli-market-latam"
            className="group inline-flex items-center gap-3 border border-[#333] px-6 py-3 font-mono text-[11px] uppercase tracking-widest text-[#AAA] hover:border-[#00FF88] hover:text-[#00FF88] transition-all duration-200"
          >
            Instalar CLI
            <span className="transition-transform duration-300 group-hover:translate-x-1">→</span>
          </a>
          <a href="#coverage"
            className="font-mono text-[11px] uppercase tracking-widest text-[#555] hover:text-[#888] transition-colors duration-200"
          >
            Cobertura ↓
          </a>
        </div>
      </div>
    </section>
  );
}
