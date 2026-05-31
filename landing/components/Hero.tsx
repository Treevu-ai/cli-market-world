"use client";
import { useEffect, useRef, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import ScrambleText from "@/components/ScrambleText";
import { MARKET_STATS } from "@/lib/marketStats";

const TERMINAL_LOOP_ES = [
  "Sync node AR_BUE_09",
  'market compare "arroz" --country MX',
  "Sync node MX_CDMX_03",
  'market search "aceite" --brand Natura',
  "Sync node BR_SAO_11",
];

const TERMINAL_LOOP_EN = [
  "Sync node AR_BUE_09",
  'market compare "rice" --country MX',
  "Sync node MX_CDMX_03",
  'market search "oil" --brand Natura',
  "Sync node BR_SAO_11",
];

export default function Hero() {
  const { lang } = useLang();
  const isES = lang === "es";
  const glowRef = useRef<HTMLDivElement>(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const [lineIndex, setLineIndex] = useState(0);
  const [visibleLines, setVisibleLines] = useState<string[]>([]);

  useEffect(() => {
    const logs = isES ? TERMINAL_LOOP_ES : TERMINAL_LOOP_EN;
    setVisibleLines([]);
    setLineIndex(0);

    const interval = setInterval(() => {
      setLineIndex((prev) => {
        const next = (prev + 1) % logs.length;
        setVisibleLines((lines) => [...lines.slice(-(logs.length - 1)), logs[prev]]);
        return next;
      });
      if (terminalRef.current) {
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
      }
    }, 3500);

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

  return (
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
          {isES ? (
            <>
              Agentes de IA y equipos de pricing buscan y comparan precios reales de góndola en{" "}
              {MARKET_STATS.retailersVerified} retailers verificados —{MARKET_STATS.retailersDefined} en catálogo— de{" "}
              {MARKET_STATS.countries} países, vía API, CLI y herramientas MCP.
            </>
          ) : (
            <>
              AI agents and pricing teams search and compare real shelf prices across{" "}
              {MARKET_STATS.retailersVerified} verified retailers —{MARKET_STATS.retailersDefined} in catalog— in{" "}
              {MARKET_STATS.countries} countries, via API, CLI, and MCP tools.
            </>
          )}
        </p>

        <div className="flex flex-col items-center justify-center gap-3">
          <a
            href="https://pypi.org/project/cli-market/"
            className="w-full sm:w-auto px-10 py-4 bg-[var(--cm-mint)] text-[var(--cm-on-mint)] font-label-caps text-sm cyber-glow-mint transition-all text-center"
          >
            <ScrambleText text={isES ? "Empezar gratis con la API" : "Start free with the API"} />
          </a>
          <p className="text-sm text-[var(--cm-on-surface-variant)]">
            <a href="#pricing-intelligence" className="hover:text-[var(--cm-mint)] transition-colors">
              {isES ? "Intelligence · piloto USD 300–500/mes" : "Intelligence · pilot USD 300–500/mo"}
            </a>
            <span className="mx-2 opacity-40">·</span>
            <a href="#retailers" className="hover:text-[var(--cm-mint)] transition-colors">
              {isES ? "Listar mi tienda (gratis)" : "List my store (free)"}
            </a>
          </p>
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
              {visibleLines.map((line, i) => (
                <div key={`${line}-${i}`} className="flex items-center gap-2">
                  <span className="opacity-40">❯</span>
                  <p>{line}</p>
                </div>
              ))}
              <div className="flex items-center gap-2">
                <span className="opacity-40">❯</span>
                <p className="text-[var(--cm-on-surface-variant)] opacity-60 animate-pulse">
                  {(isES ? TERMINAL_LOOP_ES : TERMINAL_LOOP_EN)[lineIndex]}
                </p>
              </div>
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

        {/* Product demo */}
        <div className="mt-8 w-full max-w-[900px]">
          <img
            src="/demo.gif"
            alt={isES ? "Demo: agente de IA comprando canasta básica en supermercados peruanos con CLI Market" : "Demo: AI agent shopping a basic basket at Peruvian supermarkets with CLI Market"}
            className="mx-auto rounded-xl border border-[var(--wise-green-pale)] shadow-lg max-w-full h-auto"
            width={960}
            height={540}
            loading="lazy"
          />
          <p className="text-[10px] text-[var(--wise-mute)] mt-2 font-mono text-center">
            {isES ? "Agente IA · canasta básica PE · 30 verificados · 14 s" : "AI agent · PE basic basket · 30 verified · 14 s"}
          </p>
        </div>
      </div>
    </section>
  );
}
