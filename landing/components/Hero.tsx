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
    { num: String(MARKET_STATS.mcpTools), label: isES ? "MCP" : "MCP", accent: false },
    { num: String(retailersDefined), label: isES ? `retailers (${retailersVerified} verif.)` : `retailers (${retailersVerified} verif.)`, accent: false },
    { num: String(MARKET_STATS.countries), label: isES ? "países" : "countries", accent: false },
    { num: priceChip, label: isES ? "precios" : "prices", accent: false },
    { num: `${MARKET_STATS.pricesRefreshHours}h`, label: "refresh", accent: false },
  ];

  return (
    <section id="hero" className="relative min-h-[90vh] flex flex-col bg-[var(--wise-canvas-soft)]">
      <div className="absolute left-3 md:left-4 top-1/2 -translate-y-1/2 hidden md:block">
        <span className="font-mono text-[9px] uppercase tracking-[0.3em] text-[var(--wise-mute)] -rotate-90 origin-left block whitespace-nowrap">
          {isES ? "COMERCIO" : "COMMERCE"}
        </span>
      </div>
      <div className="flex-1 flex flex-col justify-center items-center landing-container pt-20 pb-24 lg:pt-28 lg:pb-32 text-center min-w-0">
        <h1 className="text-[clamp(32px,6vw,64px)] leading-[1.0] font-black text-[var(--wise-ink)] max-w-[900px] tracking-tight">
          {isES
            ? "La capa programable del retail físico de LatAm."
            : "The programmable layer for physical retail in LatAm."}
        </h1>

        <p className="mt-5 text-base sm:text-lg text-[var(--wise-body)] max-w-[620px] leading-relaxed">
          {isES
            ? "Los agentes de IA ya buscan, comparan y compran solos. CLI Market es la API que los conecta con 30 retailers verificados en 8 países — y el canal donde tu tienda aparece ante ellos."
            : "AI agents already search, compare, and buy on their own. CLI Market is the API that connects them to 30 verified retailers across 8 countries — and the channel where your store appears to them."}
        </p>

        <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-[640px]">
          <a
            href="https://pypi.org/project/cli-market/"
            className="group flex flex-col items-center gap-2 rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] px-6 py-5 hover:bg-[var(--wise-green-hover)] transition-colors shadow-sm text-left sm:items-start"
          >
            <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--wise-ink)]/70">
              {isES ? "Para builders / agentes" : "For builders / agents"}
            </span>
            <span className="text-base font-semibold">
              <ScrambleText text={isES ? "Empezar con la API — gratis →" : "Start with the API — free →"} />
            </span>
            <code className="font-mono text-xs text-[var(--wise-ink)]/80">pip install cli-market</code>
          </a>

          <a
            href="#retailers"
            className="group flex flex-col items-center gap-2 rounded-3xl border-2 border-[var(--wise-ink)] bg-transparent text-[var(--wise-ink)] px-6 py-5 hover:bg-[var(--wise-canvas)] transition-colors text-left sm:items-start"
          >
            <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--wise-mute)]">
              {isES ? "Para retailers" : "For retailers"}
            </span>
            <span className="text-base font-semibold">
              {isES ? "Listar mi tienda — gratis →" : "List my store — free →"}
            </span>
            <span className="text-xs text-[var(--wise-mute)]">
              {isES ? "30 segundos · sin código" : "30 seconds · no code"}
            </span>
          </a>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-2">
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
      </div>
    </section>
  );
}
