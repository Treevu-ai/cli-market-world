"use client";
import { useEffect, useRef, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import ScrambleText from "@/components/ScrambleText";
import { useLiveStats } from "@/hooks/useLiveStats";
import { MARKET_STATS } from "@/lib/marketStats";

const TERMINAL_LOGS_ES = [
  "market search 'aceite' --brand 'Natura'",
  "Fetching Falabella catalog PE...",
  "Comparando 12 retailers en MX...",
  "Sync pricing node AR_BUE_09",
  "market buy ID_4402 --qty 2",
];

const TERMINAL_LOGS_EN = [
  "market search 'oil' --brand 'Natura'",
  "Fetching Falabella catalog PE...",
  "Comparing 12 retailers in MX...",
  "Sync pricing node AR_BUE_09",
  "market buy ID_4402 --qty 2",
];

export default function Hero() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { priceChip, retailersVerified, retailersDefined } = useLiveStats();
  const glowRef = useRef<HTMLDivElement>(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const [extraLines, setExtraLines] = useState<string[]>([]);

  useEffect(() => {
    const logs = isES ? TERMINAL_LOGS_ES : TERMINAL_LOGS_EN;
    const interval = setInterval(() => {
      const line = logs[Math.floor(Math.random() * logs.length)];
      setExtraLines((prev) => [...prev.slice(-4), line]);
      if (terminalRef.current) {
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
      }
    }, 4000);
    return () => clearInterval(interval);
  }, [isES]);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!glowRef.current) return;
      glowRef.current.style.transform = `translate(-50%, -50%) translate(${e.clientX / 50}px, ${e.clientY / 50}px)`;
    };
    window.addEventListener("mousemove", onMove, { passive: true });
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  const statsBar = [
    {
      label: isES ? "Retailers" : "Retailers",
      value: `${retailersDefined} (${retailersVerified} ${isES ? "verif." : "verif."})`,
    },
    { label: isES ? "Base datos" : "Database", value: `${priceChip} ${isES ? "precios" : "prices"}` },
    { label: isES ? "Cobertura" : "Coverage", value: `${MARKET_STATS.countries} ${isES ? "países" : "countries"}` },
    { label: isES ? "Integraciones" : "Integrations", value: `${MARKET_STATS.mcpTools} MCP` },
    { label: isES ? "Actualización" : "Refresh", value: `${MARKET_STATS.pricesRefreshHours}h` },
    { label: isES ? "Licencia" : "License", value: "MIT" },
  ];

  return (
    <>
      <section id="hero" className="relative min-h-[90vh] flex flex-col items-center justify-center px-[var(--cm-gutter)] overflow-hidden pt-24 pb-12">
        <div
          ref={glowRef}
          className="absolute top-1/2 left-1/2 w-[800px] h-[800px] bg-[var(--cm-mint)]/5 rounded-full blur-[120px] pointer-events-none transition-transform duration-300"
          aria-hidden="true"
        />

        <div className="relative z-10 text-center max-w-4xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 border border-[var(--cm-mint)]/30 bg-[var(--cm-mint)]/5 rounded-full mb-6">
            <span className="w-2 h-2 rounded-full bg-[var(--cm-mint)] agent-pulse" aria-hidden="true" />
            <span className="font-label-caps text-[10px] text-[var(--cm-mint)] tracking-widest">
              {isES ? "Network Engine Active" : "Network Engine Active"}
            </span>
          </div>

          <h1 className="font-display text-[clamp(2rem,5vw,4.25rem)] leading-tight mb-8 tracking-tight text-white">
            {isES ? (
              <>
                La capa programable del <span className="text-[var(--cm-mint)] italic">retail físico</span> de LatAm
              </>
            ) : (
              <>
                The programmable layer of <span className="text-[var(--cm-mint)] italic">physical retail</span> in LatAm
              </>
            )}
          </h1>

          <p className="font-sans text-lg md:text-xl text-[var(--cm-on-surface-variant)] max-w-2xl mx-auto mb-10 leading-relaxed">
            {isES
              ? "Agentes de IA buscan, comparan y compran precios en 60 retailers verificados de 8 países vía API, CLI y herramientas MCP."
              : "AI agents search, compare, and buy prices across 60 verified retailers in 8 countries via API, CLI, and MCP tools."}
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="https://pypi.org/project/cli-market/"
              className="w-full sm:w-auto px-10 py-4 bg-[var(--cm-mint)] text-[var(--cm-on-mint)] font-label-caps text-sm cyber-glow-mint transition-all text-center"
            >
              <ScrambleText text={isES ? "Empezar con la API — gratis" : "Start with the API — free"} />
            </a>
            <a
              href="#pricing-intelligence"
              className="w-full sm:w-auto px-10 py-4 glass-panel border border-white/10 hover:border-[var(--cm-mint)]/50 font-label-caps text-sm transition-all text-center"
            >
              {isES ? "Intelligence — piloto USD 300/mes" : "Intelligence — pilot USD 300/mo"}
            </a>
            <a
              href="#retailers"
              className="w-full sm:w-auto px-10 py-4 border border-white/5 hover:border-white/20 font-label-caps text-sm transition-all opacity-70 text-center"
            >
              {isES ? "Listar mi tienda — gratis" : "List my store — free"}
            </a>
          </div>
        </div>

        <div className="relative w-full max-w-5xl aspect-video mx-auto px-4 group">
          <div className="glass-panel w-full h-full min-h-[280px] rounded-xl overflow-hidden energy-border relative shadow-2xl transition-transform duration-700 group-hover:scale-[1.01]">
            <div className="header-strip w-full h-8 bg-[var(--cm-surface-container)]/50 flex items-center px-4 gap-2 border-b border-white/5">
              <div className="flex gap-1.5" aria-hidden="true">
                <div className="w-2 h-2 rounded-full bg-white/20" />
                <div className="w-2 h-2 rounded-full bg-white/20" />
                <div className="w-2 h-2 rounded-full bg-white/20" />
              </div>
              <div className="mx-auto font-mono text-[10px] text-[var(--cm-on-surface-variant)] opacity-60">
                market_agent_sh // real_time_stream
              </div>
            </div>
            <div
              ref={terminalRef}
              className="p-6 font-mono text-sm text-[var(--cm-mint)]/80 terminal-scroll overflow-y-auto h-[calc(100%-2rem)] max-h-[320px] text-left"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="opacity-40">❯</span>
                  <p>pip install cli-market</p>
                </div>
                <p className="text-[var(--cm-on-surface-variant)] opacity-40">
                  {isES ? "Installing dependencies... Done." : "Installing dependencies... Done."}
                </p>
                <div className="flex items-center gap-2">
                  <span className="opacity-40">❯</span>
                  <p>market search &quot;leche&quot; --country PE</p>
                </div>
                <div className="pl-4 border-l border-[var(--cm-mint)]/20 my-2 py-1 space-y-1">
                  <p className="text-[var(--cm-mint)] font-bold">Wong S/4.20 · Metro S/3.90 · Plaza Vea S/4.50</p>
                  <p className="text-[10px] opacity-40">
                    {isES ? "Found in 1.4s via Verified API" : "Found in 1.4s via Verified API"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="opacity-40">❯</span>
                  <p>market compare &quot;arroz&quot;</p>
                </div>
                <div className="py-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: "Retailers", value: String(retailersDefined) },
                    { label: isES ? "Precios" : "Prices", value: priceChip },
                    { label: "Refresh", value: `${MARKET_STATS.pricesRefreshHours}h` },
                    { label: isES ? "Países" : "Countries", value: String(MARKET_STATS.countries) },
                  ].map(({ label, value }) => (
                    <div key={label} className="p-4 bg-white/5 border border-white/10 rounded">
                      <div className="text-[10px] uppercase opacity-50 mb-1">{label}</div>
                      <div className="text-lg font-bold text-white">{value}</div>
                    </div>
                  ))}
                </div>
                {extraLines.map((line, i) => (
                  <div key={`${line}-${i}`} className="flex items-center gap-2">
                    <span className="opacity-40">❯</span>
                    <p className="text-[var(--cm-on-surface-variant)] opacity-40">{line}</p>
                  </div>
                ))}
                <p className="text-[var(--cm-on-surface-variant)] opacity-40 animate-pulse">
                  {isES ? "Scanning Falabella, Jumbo, Chedraui catalogs..." : "Scanning Falabella, Jumbo, Chedraui catalogs..."}
                </p>
              </div>
            </div>
          </div>

          <div
            className="absolute -top-10 -right-10 w-48 h-48 glass-panel rounded-lg energy-border hidden md:flex items-center justify-center"
            aria-hidden="true"
          >
            <div className="text-center">
              <div className="font-mono text-[10px] opacity-50 uppercase">Open Source</div>
              <div className="font-display text-[var(--cm-mint)] text-2xl font-bold">MIT</div>
            </div>
          </div>
        </div>
      </section>

      <section
        className="border-y border-[var(--cm-outline-variant)]/20 bg-[var(--cm-surface-low)] py-6"
        aria-label={isES ? "Métricas del producto" : "Product metrics"}
      >
        <div className="landing-container-wide grid grid-cols-2 md:grid-cols-6 gap-4 text-center">
          {statsBar.map(({ label, value }, i) => (
            <div key={label} className={`space-y-1 ${i > 0 ? "md:border-l md:border-white/5" : ""}`}>
              <div className="font-mono text-[10px] opacity-50 uppercase">{label}</div>
              <div className="font-semibold text-sm text-white">{value}</div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
