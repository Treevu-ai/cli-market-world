"use client";

import { useEffect, useState } from "react";
import GlitchText from "@/components/GlitchText";
import CollabCursors from "@/components/CollabCursors";

const LATAM_MAP = [
  "                   ▄▄▄▄▄▄▄                   ",
  "               ▄▄████████████▄▄               ",
  "            ▄████████████████████▄            ",
  "          ▄████████████████████████▄          ",
  "        ▄██████▀▀          ▀▀██████▄        ",
  "       ██████▌                ▐██████       ",
  "      █████                      █████      ",
  "     █████         ▄████▄         █████     ",
  "    █████        ▄████████▄        █████    ",
  "   █████       ▄████████████▄       █████   ",
  "  █████       ████████████████      █████   ",
  "  █████      ▐████████████████▌     █████   ",
  " █████       ██████████████████     █████   ",
  " █████        ████████████████      █████   ",
  "▐█████         ▀████████████▀      █████▌   ",
  " █████            ▀▀████▀▀         █████    ",
  "  █████                           █████     ",
  "    █████▌                       ▐█████     ",
  "      ██████▄▄               ▄▄██████       ",
  "         ▀█████████▄▄▄▄▄▄▄████████▀         ",
  "              ▀▀████████████▀▀              ",
];

const COUNTRY_DOTS = [
  { row: 5,  col: 18, color: "#FF6B35", label: "MX", delay: "0s" },
  { row: 8,  col: 23, color: "#FFD600", label: "CO", delay: "0.3s" },
  { row: 11, col: 20, color: "#00FF88", label: "PE", delay: "0.6s" },
  { row: 10, col: 30, color: "#4ADE80", label: "BR", delay: "0.9s" },
  { row: 17, col: 22, color: "#60A5FA", label: "AR", delay: "1.2s" },
];

export default function Hero() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <section className="relative flex flex-col items-center w-full bg-[#0A0A0A] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] overflow-hidden">
      <div className="flex items-center justify-center gap-[6px] sm:gap-[8px] h-[28px] sm:h-[32px] px-[10px] sm:px-[12px] md:px-[16px] bg-[#1A1A1A] border-2 border-[#00FF88] max-w-full">
        <div className="w-[6px] h-[6px] sm:w-[8px] sm:h-[8px] bg-[#00FF88] shrink-0" />
        <span className="font-ibm-mono text-[8px] sm:text-[9px] md:text-[11px] font-bold text-[#00FF88] tracking-[1px] md:tracking-[2px]">
          [CLI] // INFRAESTRUCTURA PARA AGENTES IA
        </span>
      </div>
      <div className="h-6 sm:h-8 md:h-[24px]" />
      <div className="flex items-center justify-center gap-[6px] h-[24px] sm:h-[28px] px-[10px] sm:px-[14px] bg-[#FFD600]/10 border border-[#FFD600]/30 mb-2">
        <span className="w-[5px] h-[5px] bg-[#FFD600] rounded-full animate-pulse" />
        <span className="font-ibm-mono text-[8px] sm:text-[9px] font-bold text-[#FFD600] tracking-[1px]">
          EARLY ADOPTER — LANZAMIENTO MAYO 2026
        </span>
      </div>
      <div className="h-6 sm:h-8 md:h-[32px]" />
      <h1 className="font-grotesk text-[clamp(26px,8vw,96px)] font-bold text-[#F5F5F0] tracking-[-0.5px] sm:tracking-[-1px] leading-none text-center w-full max-w-[1100px]">
        <GlitchText text="SUPERMERCADOS" speed={45} delay={100} /><br />
        <GlitchText text="COMO APIs." speed={45} delay={400} />
      </h1>
      <h1 className="font-grotesk text-[clamp(26px,8vw,96px)] font-bold text-[#00FF88] tracking-[-0.5px] sm:tracking-[-1px] leading-none text-center w-full max-w-[1100px]">
        <GlitchText text="PARA AGENTES IA." speed={45} delay={700} />
      </h1>
      <div className="h-6 sm:h-8 md:h-[32px]" />
      <p className="font-ibm-mono text-[11px] sm:text-[13px] md:text-[15px] text-[#888888] tracking-[0.5px] sm:tracking-[1px] leading-[1.5] sm:leading-[1.6] text-center w-full max-w-[800px] px-2">
        17 COMERCIOS · 6 LÍNEAS DE NEGOCIO · 5 PAÍSES · 1 API UNIFICADA.<br />
        STRIPE CONVIRTIÓ LOS PAGOS EN APIs. NOSOTROS CONVERTIMOS EL COMERCIO LATAM EN APIs PARA AGENTES IA.
      </p>
      <div className="h-8 sm:h-10 md:h-[48px]" />
      <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 md:gap-[16px] w-full sm:w-auto px-2 sm:px-0">
        <a href="https://github.com/Treevu-ai/cli-market-latam"
          className="flex items-center justify-center w-full sm:w-[240px] h-[52px] sm:h-[56px] bg-[#00FF88] hover:bg-[#00cc6a] active:scale-[0.98] transition-all">
          <span className="font-grotesk text-[11px] sm:text-[12px] font-bold text-[#0A0A0A] tracking-[1.5px] sm:tracking-[2px]">INSTALAR AHORA</span>
        </a>
        <button onClick={() => { const el = document.getElementById("features"); if (el) el.scrollIntoView({ behavior: "smooth" }); }}
          className="flex items-center justify-center w-full sm:w-[200px] h-[52px] sm:h-[56px] bg-[#0A0A0A] border-2 border-[#3D3D3D] hover:border-[#888888] active:scale-[0.98] transition-all cursor-pointer">
          <span className="font-ibm-mono text-[11px] sm:text-[12px] text-[#888888] tracking-[1px] sm:tracking-[2px]">VER COMANDOS →</span>
        </button>
      </div>
      <div className="h-5 sm:h-6 md:h-[24px]" />
      <p className="font-ibm-mono text-[10px] sm:text-[11px] text-[#555555] tracking-[1px] sm:tracking-[2px] text-center break-all px-4 max-w-full">
        pip install git+https://github.com/Treevu-ai/cli-market-latam.git
      </p>
      <div className="h-8 sm:h-12 md:h-[48px]" />
      <div className="w-full max-w-[680px] overflow-hidden" style={{ border: "2px solid #1A1A1A" }}>
        <LatamMapSCII mounted={mounted} />
      </div>
      <CollabCursors />
    </section>
  );
}

function LatamMapSCII({ mounted }: { mounted: boolean }) {
  if (!mounted) return null;
  return (
    <div className="bg-[#080808] p-3 sm:p-4 md:p-5 font-mono leading-[1.15] relative overflow-hidden select-none">
      <style>{`
        @keyframes scan-mapscii { 0%{top:0;opacity:0} 15%{opacity:0.35} 85%{opacity:0.35} 100%{top:100%;opacity:0} }
        @keyframes mpulse { 0%,100%{opacity:1;box-shadow:0 0 4px currentColor} 50%{opacity:0.25;box-shadow:0 0 8px currentColor} }
        .mscan-line { position:absolute; left:0; width:100%; height:1px; background:#00FF88; animation:scan-mapscii 4.5s linear infinite; z-index:5; }
        .mdot { animation:mpulse 2s ease-in-out infinite; }
      `}</style>
      <div className="mscan-line" />
      <div className="text-[7px] sm:text-[8px] md:text-[9px] text-[#333] tracking-[2px] mb-1 flex justify-between">
        <span>MAPSCII — LATAM COVERAGE</span>
        <span className="text-[#444]">┌─ TERMINAL ─┐</span>
      </div>
      <div className="relative inline-block text-[6px] sm:text-[7px] md:text-[8px]">
        <pre className="text-[#1A3D2D] leading-[1.05] m-0" style={{ fontFamily: "'IBM Plex Mono', 'Courier New', monospace" }}>
          {LATAM_MAP.join("\n")}
        </pre>
        {COUNTRY_DOTS.map((dot) => (
          <div key={dot.label} className="absolute flex items-center gap-[3px]"
            style={{
              top: `calc(${dot.row} * 1.05em + 2px)`,
              left: `calc(${dot.col} * 1ch)`,
              animationDelay: dot.delay,
            } as React.CSSProperties}
          >
            <span className="mdot inline-block w-[4px] h-[4px] sm:w-[5px] sm:h-[5px] rounded-full"
              style={{ backgroundColor: dot.color, color: dot.color }} />
            <span className="text-[#555] font-mono text-[5px] sm:text-[6px]">{dot.label}</span>
          </div>
        ))}
      </div>
      <div className="flex items-center gap-3 sm:gap-5 mt-2 pt-1.5 border-t border-[#141414] text-[6px] sm:text-[7px] md:text-[8px] font-mono">
        <span><span className="text-[#00FF88]">●</span> <span className="text-[#555]">17 STORES</span></span>
        <span><span className="text-[#FFD600]">●</span> <span className="text-[#555]">6 LINES</span></span>
        <span><span className="text-[#60A5FA]">●</span> <span className="text-[#555]">5 COUNTRIES</span></span>
        <span><span className="text-[#FF6B35]">●</span> <span className="text-[#555]">12 TOOLS</span></span>
        <span className="ml-auto text-[#333] animate-pulse">█ ONLINE</span>
      </div>
    </div>
  );
}
