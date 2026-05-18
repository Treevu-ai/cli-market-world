"use client";

import { useEffect, useState } from "react";
import GlitchText from "@/components/GlitchText";

function TerminalPreview({ mounted }: { mounted: boolean }) {
  if (!mounted) return null;
  return (
    <div className="w-full max-w-[540px] mx-auto lg:mx-0 opacity-80 hover:opacity-100 transition-opacity duration-500">
      <svg viewBox="0 0 560 420" width="100%" height="auto" style={{ display: "block" }}>
        <style>{`
          @keyframes cursor-blink { 0%,100%{opacity:1} 50%{opacity:0} }
          @keyframes fade-in { 0%{opacity:0} 100%{opacity:1} }
          .tc { animation: cursor-blink 1s step-end infinite; }
          .r1 { animation: fade-in 0.3s ease-out 0.8s both; }
          .r2 { animation: fade-in 0.3s ease-out 1.0s both; }
          .r3 { animation: fade-in 0.3s ease-out 1.2s both; }
        `}</style>
        <rect x="4" y="4" width="552" height="412" rx="8" fill="#090909" stroke="#1A1A1A" strokeWidth="1" />
        <rect x="4" y="4" width="552" height="28" rx="8" fill="#0F0F0F" />
        <rect x="4" y="22" width="552" height="10" fill="#0F0F0F" />
        <circle cx="22" cy="18" r="4" fill="#FF5F57" />
        <circle cx="38" cy="18" r="4" fill="#FEBC2E" />
        <circle cx="54" cy="18" r="4" fill="#28C840" />
        <text x="280" y="22" fontFamily="monospace" fontSize="8" fill="#333" textAnchor="middle">cli-market — bash</text>

        {/* Welcome banner */}
        <rect x="20" y="44" width="520" height="48" fill="#0D0D0D" stroke="#1A1A1A" strokeWidth="0.5" rx="2" />
        <text x="40" y="64" fontFamily="monospace" fontSize="9" fill="#FFD600" fontWeight="bold">CLI MARKET v1.0 · 100 retailers · 12 líneas</text>
        <text x="40" y="80" fontFamily="monospace" fontSize="7" fill="#444">Conectá agentes de IA con el comercio LATAM</text>

        {/* Prompt 1 */}
        <text x="32" y="118" fontFamily="monospace" fontSize="8" fill="#444">~/market</text>
        <text x="104" y="118" fontFamily="monospace" fontSize="8" fill="#888">❯</text>
        <text x="116" y="118" fontFamily="monospace" fontSize="9" fill="#00FF88" fontWeight="bold">market lines</text>

        {/* Lines output */}
        <g className="r1">
          <text x="32" y="134" fontFamily="monospace" fontSize="6" fill="#444">🛒 Supermercados 27</text>
          <text x="160" y="134" fontFamily="monospace" fontSize="6" fill="#444">📱 Electro 14</text>
          <text x="280" y="134" fontFamily="monospace" fontSize="6" fill="#444">👕 Moda 8</text>
          <text x="390" y="134" fontFamily="monospace" fontSize="6" fill="#444">⚽ Deportes 15</text>
        </g>
        <g className="r2">
          <text x="32" y="148" fontFamily="monospace" fontSize="6" fill="#444">💊 Farmacias 6</text>
          <text x="160" y="148" fontFamily="monospace" fontSize="6" fill="#444">🏠 Hogar 7</text>
          <text x="280" y="148" fontFamily="monospace" fontSize="6" fill="#444">💄 Belleza 6</text>
          <text x="390" y="148" fontFamily="monospace" fontSize="6" fill="#444">🐾 Mascotas 3</text>
        </g>

        {/* Prompt 2 */}
        <text x="32" y="172" fontFamily="monospace" fontSize="8" fill="#444">~/market</text>
        <text x="104" y="172" fontFamily="monospace" fontSize="8" fill="#888">❯</text>
        <text x="116" y="172" fontFamily="monospace" fontSize="9" fill="#FF6B35" fontWeight="bold">market search</text>
        <text x="236" y="172" fontFamily="monospace" fontSize="8" fill="#AAA">"leche"</text>
        <text x="292" y="172" fontFamily="monospace" fontSize="8" fill="#888">--country PE</text>

        <g className="r1">
          <text x="32" y="188" fontFamily="monospace" fontSize="6" fill="#555">Buscando en 3 retailers...</text>
        </g>

        {/* Search results table */}
        <g className="r2">
          <rect x="32" y="196" width="496" height="12" fill="#0F0F0F" />
          <text x="42" y="205" fontFamily="monospace" fontSize="5" fill="#555">PRODUCTO</text>
          <text x="200" y="205" fontFamily="monospace" fontSize="5" fill="#555">TIENDA</text>
          <text x="310" y="205" fontFamily="monospace" fontSize="5" fill="#555">PRECIO</text>
          <text x="400" y="205" fontFamily="monospace" fontSize="5" fill="#555">PAÍS</text>
        </g>
        <g className="r3">
          <text x="42" y="220" fontFamily="monospace" fontSize="7" fill="#CCC">Leche Gloria 400ml</text>
          <text x="200" y="220" fontFamily="monospace" fontSize="7" fill="#888">Wong</text>
          <text x="310" y="220" fontFamily="monospace" fontSize="7" fill="#FFD600">S/3.50</text>
          <text x="400" y="220" fontFamily="monospace" fontSize="7" fill="#555">🇵🇪</text>
        </g>

        {/* Prompt 3 */}
        <text x="32" y="258" fontFamily="monospace" fontSize="8" fill="#444">~/market</text>
        <text x="104" y="258" fontFamily="monospace" fontSize="8" fill="#888">❯</text>
        <text x="116" y="258" fontFamily="monospace" fontSize="9" fill="#4ADE80" fontWeight="bold">market compare</text>
        <text x="252" y="258" fontFamily="monospace" fontSize="8" fill="#AAA">"aceite"</text>

        {/* Compare table */}
        <g className="r1">
          <rect x="32" y="272" width="496" height="12" fill="#0F0F0F" />
          <text x="42" y="281" fontFamily="monospace" fontSize="5" fill="#555">PRODUCTO</text>
          <text x="250" y="281" fontFamily="monospace" fontSize="5" fill="#555">PRECIO</text>
          <text x="350" y="281" fontFamily="monospace" fontSize="5" fill="#555">TIENDA</text>
          <text x="460" y="281" fontFamily="monospace" fontSize="5" fill="#555">PAÍS</text>
        </g>
        <g className="r2"><text x="42" y="296" fontFamily="monospace" fontSize="7" fill="#CCC">Aceite Primor 1L</text><text x="250" y="296" fontFamily="monospace" fontSize="7" fill="#FFD600">S/8.90</text><text x="350" y="296" fontFamily="monospace" fontSize="7" fill="#888">Wong</text><text x="460" y="296" fontFamily="monospace" fontSize="7" fill="#555">🇵🇪</text></g>
        <g className="r2"><text x="42" y="310" fontFamily="monospace" fontSize="7" fill="#999">Aceite Natura 900ml</text><text x="250" y="310" fontFamily="monospace" fontSize="7" fill="#FFD600">ARS 1,250</text><text x="350" y="310" fontFamily="monospace" fontSize="7" fill="#888">Carrefour</text><text x="460" y="310" fontFamily="monospace" fontSize="7" fill="#555">🇦🇷</text></g>
        <g className="r2"><text x="42" y="324" fontFamily="monospace" fontSize="7" fill="#999">Aceite Liza 900ml</text><text x="250" y="324" fontFamily="monospace" fontSize="7" fill="#FFD600">R$ 6.50</text><text x="350" y="324" fontFamily="monospace" fontSize="7" fill="#888">Carrefour BR</text><text x="460" y="324" fontFamily="monospace" fontSize="7" fill="#555">🇧🇷</text></g>

        {/* Prompt 4 with cursor */}
        <text x="32" y="360" fontFamily="monospace" fontSize="8" fill="#444">~/market</text>
        <text x="104" y="360" fontFamily="monospace" fontSize="8" fill="#888">❯</text>
        <text x="116" y="360" fontFamily="monospace" fontSize="9" fill="#AAA">_</text>
        <rect x="116" y="351" width="7" height="11" fill="#00FF88" className="tc" />

        {/* Status bar */}
        <rect x="4" y="388" width="552" height="28" fill="#0F0F0F" />
        <circle cx="18" cy="402" r="3" fill="#00FF88" />
        <text x="28" y="406" fontFamily="monospace" fontSize="6" fill="#555">100 STORES</text>
        <text x="132" y="406" fontFamily="monospace" fontSize="6" fill="#444">·</text>
        <text x="142" y="406" fontFamily="monospace" fontSize="6" fill="#555">12 LINES</text>
        <text x="240" y="406" fontFamily="monospace" fontSize="6" fill="#444">·</text>
        <text x="250" y="406" fontFamily="monospace" fontSize="6" fill="#555">12 COUNTRIES</text>
        <text x="370" y="406" fontFamily="monospace" fontSize="6" fill="#444">·</text>
        <text x="380" y="406" fontFamily="monospace" fontSize="6" fill="#555">MCP ONLINE</text>
      </svg>
    </div>
  );
}

export default function Hero() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <section id="hero" className="relative min-h-screen flex items-center px-6 md:px-28 pt-20 pb-24 md:pt-32 md:pb-32 overflow-hidden">
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{
        backgroundImage: "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
        backgroundSize: "64px 64px",
      }} />
      <div className="hidden md:block absolute left-6 top-1/2 -translate-y-1/2">
        <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#444] -rotate-90 origin-left block whitespace-nowrap">CLI MARKET</span>
      </div>

      <div className="flex flex-col lg:flex-row items-start lg:items-center gap-10 lg:gap-16 w-full max-w-[1200px] mx-auto">
        <div className="flex-1 flex flex-col justify-center max-w-[520px]">
          <div className="font-grotesk text-[clamp(48px,10vw,96px)] font-bold text-[#F5F5F0] tracking-[-2px] leading-[0.9]">
            {mounted ? <GlitchText text="CLI MARKET" speed={60} delay={200} /> : "CLI MARKET"}
          </div>
          <h2 className="font-mono text-[#666] text-[clamp(12px,1.8vw,16px)] mt-4 md:mt-6 tracking-[0.15em] uppercase">
            Infraestructura de comercio para agentes de inteligencia artificial
          </h2>
          <p className="mt-6 md:mt-8 max-w-md font-mono text-[13px] md:text-[14px] text-[#888] leading-relaxed">
            100 retailers en 12 países comparten la misma API VTEX. 
            Construimos la capa de datos que ningún retailer puede construir solo.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
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
          <div className="mt-8 md:mt-12 flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-8">
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

        <div className="flex-1 w-full lg:max-w-[540px] flex justify-center lg:justify-end">
          <TerminalPreview mounted={mounted} />
        </div>
      </div>
    </section>
  );
}
