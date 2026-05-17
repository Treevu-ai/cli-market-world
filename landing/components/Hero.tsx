"use client";

import { useEffect, useState } from "react";
import GlitchText from "@/components/GlitchText";
import CollabCursors from "@/components/CollabCursors";

const codeLines = [
  { x: 318, w: 160, color: "#00FF88" },
  { x: 318, w: 200, color: "#4ADE80" },
  { x: 318, w: 140, color: "#FF6B35" },
  { x: 318, w: 180, color: "#60A5FA" },
  { x: 318, w: 120, color: "#FFD600" },
  { x: 318, w: 210, color: "#00FF88" },
  { x: 318, w: 170, color: "#888888" },
  { x: 318, w: 90, color: "#F5F5F0" },
];

const tickerItems = [
  "WONG", "METRO", "PLAZA VEA", "CARREFOUR", "JUMBO",
  "CHEDRAUI", "HEB", "OLIMPICA", "OPEN FOOD FACTS",
];

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

      {/* Headline */}
      <h1 className="font-grotesk text-[clamp(26px,8vw,96px)] font-bold text-[#F5F5F0] tracking-[-0.5px] sm:tracking-[-1px] leading-none text-center w-full max-w-[1100px]">
        <GlitchText text="SUPERMERCADOS" speed={45} delay={100} />
        <br />
        <GlitchText text="COMO APIs." speed={45} delay={400} />
      </h1>
      <h1 className="font-grotesk text-[clamp(26px,8vw,96px)] font-bold text-[#00FF88] tracking-[-0.5px] sm:tracking-[-1px] leading-none text-center w-full max-w-[1100px]">
        <GlitchText text="PARA AGENTES IA." speed={45} delay={700} />
      </h1>

      <div className="h-6 sm:h-8 md:h-[32px]" />

      <p className="font-ibm-mono text-[11px] sm:text-[13px] md:text-[15px] text-[#888888] tracking-[0.5px] sm:tracking-[1px] leading-[1.5] sm:leading-[1.6] text-center w-full max-w-[800px] px-2">
        8 SUPERMERCADOS · 5 PAÍSES · 1 API UNIFICADA.
        <br />
        STRIPE CONVIRTIÓ LOS PAGOS EN APIs. NOSOTROS CONVERTIMOS LOS SUPERMERCADOS EN APIs.
      </p>

      <div className="h-8 sm:h-10 md:h-[48px]" />

      {/* CTAs */}
      <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 md:gap-[16px] w-full sm:w-auto px-4 sm:px-0">
        <button className="flex items-center justify-center w-full sm:w-[240px] h-[52px] sm:h-[56px] bg-[#00FF88] hover:bg-[#00cc6a] transition-colors">
          <span className="font-grotesk text-[11px] sm:text-[12px] font-bold text-[#0A0A0A] tracking-[1.5px] sm:tracking-[2px]">
            INSTALAR AHORA
          </span>
        </button>
        <button className="flex items-center justify-center w-full sm:w-[200px] h-[52px] sm:h-[56px] bg-[#0A0A0A] border-2 border-[#3D3D3D] hover:border-[#888888] transition-colors">
          <span className="font-ibm-mono text-[11px] sm:text-[12px] text-[#888888] tracking-[1.5px] sm:tracking-[2px]">
            VER COMANDOS &gt;
          </span>
        </button>
      </div>

      <div className="h-5 sm:h-6 md:h-[24px]" />

      <p className="font-ibm-mono text-[10px] sm:text-[11px] text-[#555555] tracking-[1px] sm:tracking-[2px] text-center break-all px-4 max-w-full">
        pip install git+https://github.com/Treevu-ai/cli-market-latam.git
      </p>

      <div className="h-8 sm:h-12 md:h-[64px]" />

      {/* Terminal CLI Interface SVG */}
      <div
        className="hidden sm:block w-full max-w-[1100px] bg-[#0F0F0F] overflow-hidden"
        style={{ border: "2px solid #2D2D2D" }}
      >
        <TerminalSVG mounted={mounted} />
      </div>

      <CollabCursors />
    </section>
  );
}

function TerminalSVG({ mounted }: { mounted: boolean }) {
  if (!mounted) return null;

  const rows = [
    { cmd: "$ market search \"leche\"",     color: "#00FF88" },
    { cmd: "",                               color: "" },
    { cmd: "🔍 Buscando en 8 tiendas...",   color: "#888" },
    { cmd: "",                               color: "" },
    { cmd: "Wong       | Leche Gloria 400ml  | S/ 3.50", color: "#F5F5F0" },
    { cmd: "Metro      | Leche Gloria 400ml  | S/ 3.80", color: "#888" },
    { cmd: "Plaza Vea  | Leche Gloria 400ml  | S/ 3.60", color: "#F5F5F0" },
    { cmd: "Carrefour  | Leche La Serenísima | ARS 890",  color: "#888" },
    { cmd: "Jumbo      | Leche La Serenísima | ARS 920",  color: "#F5F5F0" },
  ];

  return (
    <>
      <svg
        viewBox="0 0 900 540"
        width="100%"
        height="auto"
        style={{ display: "block" }}
      >
        <style>
          {mounted ? `
            .hero-cursor { animation: hero-blink 1s step-end infinite; }
            @keyframes hero-blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
            .hero-ticker-track { animation: hero-scroll 25s linear infinite; }
            @keyframes hero-scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-630px); } }
            .hero-pulse { animation: hero-pulse 2s ease-in-out infinite; }
            @keyframes hero-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
          ` : ""}
        </style>

        {/* Terminal window */}
        <rect x="100" y="20" width="700" height="500" rx="8" fill="#0D0D0D" stroke="#1E1E1E" strokeWidth="1" />
        <rect x="100" y="20" width="700" height="32" rx="8" fill="#111" />
        <circle cx="120" cy="36" r="5" fill="#FF5F57" />
        <circle cx="140" cy="36" r="5" fill="#FEBC2E" />
        <circle cx="160" cy="36" r="5" fill="#28C840" />
        <text x="200" y="40" fontFamily="monospace" fontSize="10" fill="#555" letterSpacing={1}>cli-market-latam — bash</text>

        {/* Terminal content */}
        {rows.map((row, i) => (
          <text
            key={`row${i}`}
            x="120"
            y={75 + i * 22}
            fontFamily="monospace"
            fontSize="12"
            fill={row.color}
            letterSpacing={0.5}
          >
            {row.cmd}
          </text>
        ))}

        {/* Cursor */}
        <rect className="hero-cursor" x="310" y="280" width="8" height="14" fill="#00FF88" />

        {/* Sidebar directory tree */}
        <rect x="20" y="80" width="180" height="180" fill="#0D0D0D" stroke="#1E1E1E" strokeWidth="0.5" rx="4" />
        <text x="32" y="100" fontFamily="monospace" fontSize="8" fill="#555" letterSpacing={1}>📁 market-cli/</text>
        <text x="44" y="116" fontFamily="monospace" fontSize="7" fill="#444" letterSpacing={0.5}>├── market search</text>
        <text x="44" y="130" fontFamily="monospace" fontSize="7" fill="#444" letterSpacing={0.5}>├── market compare</text>
        <text x="44" y="144" fontFamily="monospace" fontSize="7" fill="#444" letterSpacing={0.5}>├── market add</text>
        <text x="44" y="158" fontFamily="monospace" fontSize="7" fill="#444" letterSpacing={0.5}>├── market cart</text>
        <text x="44" y="172" fontFamily="monospace" fontSize="7" fill="#444" letterSpacing={0.5}>├── market checkout</text>
        <text x="44" y="186" fontFamily="monospace" fontSize="7" fill="#444" letterSpacing={0.5}>├── market orders</text>
        <text x="44" y="200" fontFamily="monospace" fontSize="7" fill="#444" letterSpacing={0.5}>├── market ask</text>
        <text x="44" y="214" fontFamily="monospace" fontSize="7" fill="#00FF88" letterSpacing={0.5}>├── market --json</text>
        <text x="44" y="228" fontFamily="monospace" fontSize="7" fill="#444" letterSpacing={0.5}>└── market about</text>

        {/* Architecture diagram */}
        <text x="32" y="256" fontFamily="monospace" fontSize="8" fill="#555" letterSpacing={1}>📊 ARQUITECTURA</text>
        <rect x="32" y="264" width="80" height="18" rx="2" fill="#1A1A1A" stroke="#333" strokeWidth="0.5" />
        <text x="36" y="276" fontFamily="monospace" fontSize="6" fill="#888" letterSpacing={0.5}>Retail VTEX</text>

        <line x1="72" y1="282" x2="72" y2="292" stroke="#333" strokeWidth="0.5" />
        <rect x="32" y="292" width="80" height="18" rx="2" fill="#0D0D0D" stroke="#00FF88" strokeWidth="1" />
        <text x="36" y="304" fontFamily="monospace" fontSize="6" fill="#00FF88" letterSpacing={0.5}>CLI Market</text>

        <line x1="72" y1="310" x2="72" y2="322" stroke="#333" strokeWidth="0.5" />
        <rect x="32" y="322" width="80" height="18" rx="2" fill="#1A1A1A" stroke="#333" strokeWidth="0.5" />
        <text x="36" y="334" fontFamily="monospace" fontSize="6" fill="#888" letterSpacing={0.5}>MCP / REST</text>

        <line x1="72" y1="340" x2="72" y2="352" stroke="#333" strokeWidth="0.5" />
        <rect x="32" y="352" width="80" height="18" rx="2" fill="#1A1A1A" stroke="#FF6B35" strokeWidth="0.5" />
        <text x="36" y="364" fontFamily="monospace" fontSize="6" fill="#FF6B35" letterSpacing={0.5}>Agentes IA</text>

        {/* Chart area */}
        <rect x="220" y="80" width="140" height="60" fill="#0D0D0D" stroke="#1E1E1E" strokeWidth="0.5" rx="4" />
        <text x="230" y="96" fontFamily="monospace" fontSize="7" fill="#555" letterSpacing={0.5}>📈 BÚSQUEDA</text>
        <rect x="230" y="102" width="20" height="24" fill="#00FF88" opacity="0.8" />
        <rect x="254" y="108" width="20" height="18" fill="#4ADE80" opacity="0.6" />
        <rect x="278" y="112" width="20" height="14" fill="#60A5FA" opacity="0.6" />
        <rect x="302" y="98" width="20" height="28" fill="#FF6B35" opacity="0.6" />
        <rect x="326" y="106" width="20" height="20" fill="#FFD600" opacity="0.6" />

        {/* Map area */}
        <rect x="370" y="80" width="200" height="60" fill="#0D0D0D" stroke="#1E1E1E" strokeWidth="0.5" rx="4" />
        <text x="380" y="96" fontFamily="monospace" fontSize="7" fill="#555" letterSpacing={0.5}>🌎 COBERTURA LATAM</text>
        <circle cx="400" cy="118" r="3" fill="#FFD600" />
        <text x="406" y="121" fontFamily="monospace" fontSize="6" fill="#888">PE</text>
        <circle cx="440" cy="114" r="3" fill="#FFD600" />
        <text x="446" y="117" fontFamily="monospace" fontSize="6" fill="#888">CO</text>
        <circle cx="480" cy="130" r="3" fill="#4ADE80" />
        <text x="486" y="133" fontFamily="monospace" fontSize="6" fill="#888">BR</text>
        <circle cx="520" cy="110" r="3" fill="#FF6B35" />
        <text x="526" y="113" fontFamily="monospace" fontSize="6" fill="#888">MX</text>
        <circle cx="460" cy="134" r="3" fill="#60A5FA" />
        <text x="466" y="137" fontFamily="monospace" fontSize="6" fill="#888">AR</text>

        {/* Stats cards */}
        <rect x="580" y="80" width="100" height="28" fill="#111" stroke="#2D2D2D" strokeWidth="0.5" rx="2" />
        <text x="590" y="97" fontFamily="monospace" fontSize="8" fill="#00FF88" fontWeight="700">8 TIENDAS</text>

        <rect x="690" y="80" width="90" height="28" fill="#111" stroke="#2D2D2D" strokeWidth="0.5" rx="2" />
        <text x="700" y="97" fontFamily="monospace" fontSize="8" fill="#FFD600" fontWeight="700">5 PAÍSES</text>

        {/* Bottom ticker */}
        <line x1="100" y1="470" x2="800" y2="470" stroke="#1E1E1E" strokeWidth="1" />
        <rect x="100" y="471" width="700" height="28" fill="#0A0A0A" />
        <clipPath id="tickerClipHero">
          <rect x="100" y="471" width="700" height="28" />
        </clipPath>
        <g clipPath="url(#tickerClipHero)">
          <g className="hero-ticker-track">
            {[...tickerItems, ...tickerItems].map((name, i) => (
              <text
                key={`t${i}`}
                x={120 + i * 80}
                y="490"
                fontFamily="monospace"
                fontSize="8"
                fill="#444"
                letterSpacing={1.5}
              >
                {name}
              </text>
            ))}
          </g>
        </g>

        {/* Status bar */}
        <line x1="100" y1="500" x2="800" y2="500" stroke="#1E1E1E" strokeWidth="1" />
        <rect x="100" y="501" width="700" height="19" rx="0" fill="#0A0A0A" />
        <circle cx="120" cy="510" r="3" fill="#00FF88" />
        <circle cx="120" cy="510" r="3" fill="#00FF88" className="hero-pulse" />
        <text x="130" y="514" fontFamily="monospace" fontSize="7" fill="#555" letterSpacing={1}>MCP ONLINE</text>
        <text x="240" y="514" fontFamily="monospace" fontSize="7" fill="#333" letterSpacing={1}>9 HERRAMIENTAS</text>
        <text x="390" y="514" fontFamily="monospace" fontSize="7" fill="#333" letterSpacing={1}>VTEX COMPATIBLE</text>
        <text x="530" y="514" fontFamily="monospace" fontSize="7" fill="#333" letterSpacing={1}>JSON PARSEABLE</text>
        <text x="680" y="514" fontFamily="monospace" fontSize="7" fill="#333" letterSpacing={1}>v1.0</text>
      </svg>
    </>
  );
}
