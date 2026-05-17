"use client";

import { useEffect, useState } from "react";
import GlitchText from "@/components/GlitchText";
import CollabCursors from "@/components/CollabCursors";

export default function Hero() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <section className="relative flex flex-col items-center w-full bg-[#0A0A0A] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px] overflow-hidden">
      {/* Badge */}
      <div className="flex items-center justify-center gap-[6px] sm:gap-[8px] h-[28px] sm:h-[32px] px-[10px] sm:px-[12px] md:px-[16px] bg-[#1A1A1A] border-2 border-[#00FF88] max-w-full">
        <div className="w-[6px] h-[6px] sm:w-[8px] sm:h-[8px] bg-[#00FF88] shrink-0" />
        <span className="font-ibm-mono text-[8px] sm:text-[9px] md:text-[11px] font-bold text-[#00FF88] tracking-[1px] md:tracking-[2px]">
          [CLI] // INFRAESTRUCTURA PARA AGENTES IA
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
      <div className="w-full max-w-[900px] overflow-hidden" style={{ border: "2px solid #1A1A1A" }}>
        <LatamMapSVG mounted={mounted} />
      </div>
      <CollabCursors />
    </section>
  );
}

function LatamMapSVG({ mounted }: { mounted: boolean }) {
  if (!mounted) return null;
  return (
    <svg viewBox="0 0 480 300" width="100%" height="auto" style={{ display: "block" }}>
      <style>{`
        @keyframes dot-pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes scan-line { 0%{transform:translateY(0);opacity:0} 15%{opacity:0.4} 85%{opacity:0.4} 100%{transform:translateY(280px);opacity:0} }
        @keyframes grid-shift { 0%,100%{opacity:0.12} 50%{opacity:0.2} }
        .dmx{animation:dot-pulse 2.2s ease-in-out infinite}
        .dco{animation:dot-pulse 2.4s ease-in-out infinite;animation-delay:0.3s}
        .dpe{animation:dot-pulse 2.0s ease-in-out infinite;animation-delay:0.6s}
        .dbr{animation:dot-pulse 2.6s ease-in-out infinite;animation-delay:0.9s}
        .dar{animation:dot-pulse 2.3s ease-in-out infinite;animation-delay:1.2s}
        .mgrid{animation:grid-shift 4s ease-in-out infinite}
        .mscan{animation:scan-line 5s linear infinite}
      `}</style>
      <rect width="480" height="300" fill="#080808" />
      <defs><pattern id="g" width="16" height="16" patternUnits="userSpaceOnUse"><path d="M 16 0 L 0 0 0 16" fill="none" stroke="#141414" strokeWidth="0.3" /></pattern></defs>
      <rect width="480" height="300" fill="url(#g)" className="mgrid" />
      <line x1="0" y1="0" x2="480" y2="0" stroke="#00FF88" strokeWidth="0.6" opacity="0" className="mscan" />
      <g fill="none" stroke="#1D3D2D" strokeWidth="0.7" opacity="0.6">
        <path d="M50,50 L70,45 L85,48 L95,42 L105,48 L98,56 L80,58 L65,54 L50,50 Z" />
        <path d="M98,56 L110,62 L118,66 L112,74 L105,68 L98,56 Z" />
        <path d="M112,74 L128,68 L148,65 L168,62 L188,64 L208,70 L222,78 L232,90 L238,105 L242,122 L238,140 L232,155 L220,168 L210,178 L195,185 L175,190 L158,188 L142,183 L132,172 L126,158 L120,142 L116,126 L114,108 L112,94 Z" />
        <path d="M112,74 L120,64 L126,68 L122,78 L112,74 Z" />
        <path d="M158,188 L168,192 L162,202 L150,210 L140,205 L145,196 L152,190 Z" />
      </g>
      <circle cx="82" cy="48" r="3" fill="#FF6B35" className="dmx" />
      <circle cx="82" cy="48" r="7" fill="#FF6B35" opacity="0.08" className="dmx" />
      <circle cx="118" cy="76" r="3" fill="#FFD600" className="dco" />
      <circle cx="118" cy="76" r="7" fill="#FFD600" opacity="0.08" className="dco" />
      <circle cx="130" cy="120" r="3" fill="#00FF88" className="dpe" />
      <circle cx="130" cy="120" r="7" fill="#00FF88" opacity="0.08" className="dpe" />
      <circle cx="198" cy="108" r="3" fill="#4ADE80" className="dbr" />
      <circle cx="198" cy="108" r="7" fill="#4ADE80" opacity="0.08" className="dbr" />
      <circle cx="155" cy="195" r="3" fill="#60A5FA" className="dar" />
      <circle cx="155" cy="195" r="7" fill="#60A5FA" opacity="0.08" className="dar" />
      <text x="88" y="50" fontFamily="monospace" fontSize="5.5" fill="#555" letterSpacing="1">MX</text>
      <text x="124" y="79" fontFamily="monospace" fontSize="5.5" fill="#555" letterSpacing="1">CO</text>
      <text x="136" y="123" fontFamily="monospace" fontSize="5.5" fill="#00FF88" letterSpacing="1">PE</text>
      <text x="204" y="111" fontFamily="monospace" fontSize="5.5" fill="#4ADE80" letterSpacing="1">BR</text>
      <text x="161" y="198" fontFamily="monospace" fontSize="5.5" fill="#555" letterSpacing="1">AR</text>
      <rect x="320" y="12" width="150" height="84" fill="#0A0A0A" stroke="#1A1A1A" strokeWidth="0.5" rx="3" opacity="0.92" />
      <text x="332" y="26" fontFamily="monospace" fontSize="5.5" fill="#444" letterSpacing="1">SYS STATUS</text>
      <line x1="332" y1="30" x2="458" y2="30" stroke="#141414" strokeWidth="0.5" />
      <text x="332" y="42" fontFamily="monospace" fontSize="5.5" fill="#777">COMERCIOS</text>
      <text x="448" y="42" fontFamily="monospace" fontSize="5.5" fill="#00FF88" textAnchor="end">17</text>
      <text x="332" y="54" fontFamily="monospace" fontSize="5.5" fill="#777">LÍNEAS</text>
      <text x="448" y="54" fontFamily="monospace" fontSize="5.5" fill="#FFD600" textAnchor="end">6</text>
      <text x="332" y="66" fontFamily="monospace" fontSize="5.5" fill="#777">PAÍSES</text>
      <text x="448" y="66" fontFamily="monospace" fontSize="5.5" fill="#60A5FA" textAnchor="end">5</text>
      <text x="332" y="78" fontFamily="monospace" fontSize="5.5" fill="#777">MCP TOOLS</text>
      <text x="448" y="78" fontFamily="monospace" fontSize="5.5" fill="#FF6B35" textAnchor="end">12</text>
      <line x1="0" y1="288" x2="480" y2="288" stroke="#141414" strokeWidth="0.5" />
      <text x="8" y="297" fontFamily="monospace" fontSize="5" fill="#222">WONG · METRO · PLAZA VEA · CARREFOUR · JUMBO · CHEDRAUI · HEB · OLÍMPICA · ÉXITO · DROGA RAIA · MAGAZINE LUIZA · RENNER · CENTAURO · HOMECENTER</text>
    </svg>
  );
}
