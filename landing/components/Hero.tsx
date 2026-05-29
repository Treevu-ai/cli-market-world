"use client";
import { useLang } from "@/lib/LanguageContext";
import ScrambleText from "@/components/ScrambleText";
import { useLiveStats } from "@/hooks/useLiveStats";
import { MARKET_STATS } from "@/lib/marketStats";

export default function Hero() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { priceChip, retailersVerified, retailersDefined } = useLiveStats();

  const chips = [
    { num: String(MARKET_STATS.mcpTools), label: isES ? "herramientas MCP" : "MCP tools", accent: false },
    { num: String(retailersDefined), label: isES ? `retailers (${retailersVerified} verificados)` : `retailers (${retailersVerified} verified)`, accent: false },
    { num: String(MARKET_STATS.countries), label: isES ? "países" : "countries", accent: false },
    { num: String(MARKET_STATS.platforms), label: isES ? "plataformas" : "platforms", accent: false },
    { num: priceChip, label: isES ? "precios verificados" : "verified prices", accent: false },
    { num: `${MARKET_STATS.pricesRefreshHours}h`, label: isES ? "refresh" : "refresh", accent: false },
  ];

  return (
    <section id="hero" className="relative min-h-[90vh] flex flex-col bg-[var(--wise-canvas-soft)]">
      <div className="absolute left-3 md:left-4 top-1/2 -translate-y-1/2 hidden md:block">
        <span className="font-mono text-[9px] uppercase tracking-[0.3em] text-[var(--wise-mute)] -rotate-90 origin-left block whitespace-nowrap">
          {isES ? "COMERCIO" : "COMMERCE"}
        </span>
      </div>
      <div className="flex-1 flex flex-col justify-center items-center px-6 py-24 lg:py-32 text-center">
        <h1 className="text-[clamp(36px,7vw,72px)] leading-[0.95] font-black text-[var(--wise-ink)] max-w-[900px] tracking-tight">
          {isES
            ? "La economía de los agentes ya empezó.\nTu negocio, adentro o afuera."
            : "The agent economy is here.\nIs your business inside or out?"}
        </h1>

        <p className="mt-4 text-base sm:text-lg text-[var(--wise-body)] max-w-[560px] leading-relaxed">
          {isES
            ? "Los agentes de IA ya buscan, comparan y compran productos sin intervención humana. CLI Market es el índice donde te encuentran. Si no estás aquí, no existes para ellos."
            : "AI agents already search, compare, and buy products without human input. CLI Market is the index where they find you. If you're not here, you don't exist to them."}
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
          {chips.map((c) => (
            <span key={c.label} className="inline-flex items-center gap-1.5 bg-[var(--wise-canvas)] rounded-3xl px-4 py-2 text-sm border border-[var(--wise-green-pale)]">
              <strong className="text-[var(--wise-ink)] tabular-nums">{c.num}</strong>
              <span className="text-[var(--wise-mute)]">{c.label}</span>
            </span>
          ))}
          <span className="inline-flex items-center rounded-3xl px-4 py-2 text-sm border border-[var(--wise-green-pale)] bg-[var(--wise-canvas)]">
            <span className="text-[var(--wise-body)] font-medium">{isES ? "Open source · MIT" : "Open source · MIT"}</span>
          </span>
        </div>

        <div className="mt-10 flex flex-col sm:flex-row items-center gap-3">
          <a
            href="#retailers"
            className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 hover:bg-[var(--wise-green-hover)] transition-colors shadow-sm"
          >
            <ScrambleText text={isES ? "Listar mi tienda →" : "List my store →"} />
          </a>
          <a
            href="https://pypi.org/project/cli-market/"
            className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-ink)] text-[var(--wise-canvas)] text-base font-semibold px-8 py-3.5 hover:opacity-90 transition-opacity"
          >
            {isES ? "Instalar gratis →" : "Install free →"}
          </a>
        </div>
      </div>

      <div className="pb-8 flex justify-center">
        <div className="inline-flex items-center gap-2 bg-[var(--wise-canvas)] rounded-3xl px-5 py-3 shadow-sm border border-[var(--wise-green-pale)]">
          <span className="w-3 h-3 rounded-full bg-[#d03238]" aria-hidden="true" />
          <span className="w-3 h-3 rounded-full bg-[#ffd11a]" aria-hidden="true" />
          <span className="w-3 h-3 rounded-full bg-[#2ead4b]" aria-hidden="true" />
          <code className="font-mono text-sm text-[var(--wise-body)] ml-3">pip install cli-market</code>
        </div>
      </div>
    </section>
  );
}
