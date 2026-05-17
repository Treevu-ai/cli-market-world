"use client";

import { useEffect, useState } from "react";
import GlitchText from "@/components/GlitchText";
import CollabCursors from "@/components/CollabCursors";

export default function Hero() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <section className="relative flex flex-col items-center w-full bg-[#0A0A0A] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] overflow-hidden group">
      {/* Hover glow — radial green light at top center */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"
        style={{ background: "radial-gradient(ellipse at 50% 30%, rgba(0,255,136,0.04) 0%, transparent 60%)" }} />

      <div className="flex items-center justify-center gap-[6px] sm:gap-[8px] h-[28px] sm:h-[32px] px-[10px] sm:px-[12px] md:px-[16px] bg-[#1A1A1A] border-2 border-[#00FF88] max-w-full group-hover:border-[#00FF88]/80 transition-colors duration-500">
        <div className="w-[6px] h-[6px] sm:w-[8px] sm:h-[8px] bg-[#00FF88] shrink-0" />
        <span className="font-ibm-mono text-[8px] sm:text-[9px] md:text-[11px] font-bold text-[#00FF88] tracking-[1px] md:tracking-[2px]">
          [CLI] // INFRAESTRUCTURA PARA AGENTES IA
        </span>
      </div>
      <div className="h-6 sm:h-8 md:h-[24px]" />
      <div className="flex items-center justify-center gap-[6px] h-[24px] sm:h-[28px] px-[10px] sm:px-[14px] bg-[#FFD600]/10 border border-[#FFD600]/30 mb-2 group-hover:bg-[#FFD600]/15 transition-colors duration-500">
        <span className="w-[5px] h-[5px] bg-[#FFD600] rounded-full animate-pulse" />
        <span className="font-ibm-mono text-[8px] sm:text-[9px] font-bold text-[#FFD600] tracking-[1px]">
          EARLY ADOPTER — LANZAMIENTO MAYO 2026
        </span>
      </div>
      <div className="h-6 sm:h-8 md:h-[32px]" />
      <h1 className="font-grotesk text-[clamp(26px,8vw,96px)] font-bold text-[#F5F5F0] tracking-[-0.5px] sm:tracking-[-1px] leading-none text-center w-full max-w-[1100px] group-hover:text-white transition-colors duration-500">
        <GlitchText text="SUPERMERCADOS" speed={45} delay={100} /><br />
        <GlitchText text="COMO APIs." speed={45} delay={400} />
      </h1>
      <h1 className="font-grotesk text-[clamp(26px,8vw,96px)] font-bold text-[#00FF88] tracking-[-0.5px] sm:tracking-[-1px] leading-none text-center w-full max-w-[1100px]">
        <GlitchText text="PARA AGENTES IA." speed={45} delay={700} />
      </h1>
      <div className="h-6 sm:h-8 md:h-[32px]" />
      <p className="font-ibm-mono text-[11px] sm:text-[13px] md:text-[15px] text-[#888888] tracking-[0.5px] sm:tracking-[1px] leading-[1.5] sm:leading-[1.6] text-center w-full max-w-[800px] px-2 group-hover:text-[#AAAAAA] transition-colors duration-500">
        100 COMERCIOS · 12 LÍNEAS · 10 PAÍSES · 1 API UNIFICADA.<br />
        UN PRODUCTO PENSADO PARA HUMANOS. DISEÑADO PARA AGENTES.
      </p>
      <div className="h-8 sm:h-10 md:h-[48px]" />
      <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 md:gap-[16px] w-full sm:w-auto px-2 sm:px-0">
        <a href="https://github.com/Treevu-ai/cli-market-latam"
          className="flex items-center justify-center w-full sm:w-[240px] h-[52px] sm:h-[56px] bg-[#00FF88] hover:bg-[#00cc6a] active:scale-[0.98] transition-all group-hover:shadow-[0_0_24px_rgba(0,255,136,0.2)]">
          <span className="font-grotesk text-[11px] sm:text-[12px] font-bold text-[#0A0A0A] tracking-[1.5px] sm:tracking-[2px]">INSTALAR AHORA</span>
        </a>
        <button onClick={() => { const el = document.getElementById("features"); if (el) el.scrollIntoView({ behavior: "smooth" }); }}
          className="flex items-center justify-center w-full sm:w-[200px] h-[52px] sm:h-[56px] bg-[#0A0A0A] border-2 border-[#3D3D3D] hover:border-[#888888] active:scale-[0.98] transition-all cursor-pointer group-hover:border-[#555]">
          <span className="font-ibm-mono text-[11px] sm:text-[12px] text-[#888888] tracking-[1px] sm:tracking-[2px] group-hover:text-[#BBBBBB] transition-colors">VER COMANDOS →</span>
        </button>
      </div>
      <div className="h-5 sm:h-6 md:h-[24px]" />
      <p className="font-ibm-mono text-[10px] sm:text-[11px] text-[#555555] tracking-[1px] sm:tracking-[2px] text-center break-all px-4 max-w-full group-hover:text-[#777] transition-colors duration-500">
        pip install git+https://github.com/Treevu-ai/cli-market-latam.git
      </p>
      <CollabCursors />
    </section>
  );
}
