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
    <section id="hero" className="landing-section relative min-h-[90vh] flex flex-col overflow-hidden animate-fade-in">
      {/* Aura glow behind title */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-[var(--cm-mint)]/5 blur-[120px]" />
        <div className="absolute top-1/2 left-1/3 w-[400px] h-[400px] rounded-full bg-[var(--cm-mint)]/8 blur-[100px]" />
      </div>

      <div className="absolute left-3 md:left-4 top-1/2 -translate-y-1/2 hidden md:block">
        <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[var(--cm-on-surface-variant)]/60 -rotate-90 origin-left block whitespace-nowrap">
          {isES ? "COMERCIO" : "COMMERCE"}
        </span>
      </div>
      <div className="flex-1 flex flex-col justify-center items-center landing-container pt-20 pb-24 lg:pt-28 lg:pb-32 text-center min-w-0 relative z-10">
        <h1 className="text-[clamp(32px,6vw,64px)] leading-[1.0] font-black text-white max-w-[900px] tracking-tight">
          {isES
            ? "La capa programable del retail físico de LatAm."
            : "The programmable layer for physical retail in LatAm."}
        </h1>

        <p className="mt-5 text-base sm:text-lg text-[var(--cm-on-surface-variant)] max-w-[620px] leading-relaxed">
          {isES
            ? "Los agentes de IA ya buscan y comparan en LATAM. CLI Market conecta builders con 30 retailers verificados — y entrega datos de precios para equipos comerciales."
            : "AI agents already search and compare across LatAm. CLI Market connects builders to 30 verified retailers — and delivers price data for commercial teams."}
        </p>

        <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-[960px]">
          <a
            href="https://pypi.org/project/cli-market/"
            className="group flex flex-col items-center gap-2 rounded-2xl bg-[var(--cm-mint)] text-[var(--cm-on-mint)] px-6 py-5 hover:brightness-110 hover:scale-[1.02] transition-all duration-200 text-left sm:items-start"
          >
            <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-on-mint)]/70">
              {isES ? "Para builders / agentes" : "For builders / agents"}
            </span>
            <span className="text-base font-semibold">
              <ScrambleText text={isES ? "Empezar con la API — gratis →" : "Start with the API — free →"} />
            </span>
            <code className="font-mono text-xs text-[var(--cm-on-mint)]/80">pip install cli-market</code>
          </a>

          <a
            href="#pricing-intelligence"
            className="group flex flex-col items-center gap-2 rounded-2xl bg-white/5 border border-white/10 px-6 py-5 hover:bg-white/10 hover:scale-[1.02] transition-all duration-200 text-left sm:items-start"
          >
            <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-mint)]">
              {isES ? "Para pricing / trade" : "For pricing / trade"}
            </span>
            <span className="text-base font-semibold text-white">
              {isES ? "Intelligence — piloto →" : "Intelligence — pilot →"}
            </span>
            <span className="text-xs text-[var(--cm-on-surface-variant)]">
              {isES ? "Desde USD 300/mes · datos verificados" : "From USD 300/mo · verified data"}
            </span>
          </a>

          <a
            href="#retailers"
            className="group flex flex-col items-center gap-2 rounded-2xl border border-[var(--cm-outline-variant)]/40 bg-transparent px-6 py-5 hover:bg-white/5 hover:scale-[1.02] transition-all duration-200 text-left sm:items-start"
          >
            <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-on-surface-variant)]">
              {isES ? "Para retailers" : "For retailers"}
            </span>
            <span className="text-base font-semibold text-white">
              {isES ? "Listar mi tienda — gratis →" : "List my store — free →"}
            </span>
            <span className="text-xs text-[var(--cm-on-surface-variant)]">
              {isES ? "30 segundos · sin código" : "30 seconds · no code"}
            </span>
          </a>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-2">
          {chips.map((c) => (
            <span key={c.label} className="inline-flex items-center gap-1.5 bg-white/5 border border-[var(--cm-outline-variant)]/30 rounded-3xl px-4 py-2 text-sm">
              <strong className="text-white tabular-nums">{c.num}</strong>
              <span className="text-[var(--cm-on-surface-variant)]">{c.label}</span>
            </span>
          ))}
          <span className="inline-flex items-center rounded-3xl px-4 py-2 text-sm border border-[var(--cm-outline-variant)]/30 bg-white/5">
            <span className="text-[var(--cm-on-surface-variant)] font-medium">{isES ? "Open source · MIT" : "Open source · MIT"}</span>
          </span>
        </div>

        {/* Product demo */}
        <div className="mt-8 w-full max-w-[900px]">
          <img
            src="/demo.gif"
            alt={isES ? "Demo: agente de IA comprando canasta básica en supermercados peruanos con CLI Market" : "Demo: AI agent shopping a basic basket at Peruvian supermarkets with CLI Market"}
            className="mx-auto rounded-xl border border-[var(--cm-outline-variant)]/40 shadow-lg max-w-full h-auto"
            width={960}
            height={540}
            loading="lazy"
          />
          <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-2 font-mono text-center">
            {isES ? "Agente IA · canasta básica PE · 30 verificados · 14 s" : "AI agent · PE basic basket · 30 verified · 14 s"}
          </p>
        </div>
      </div>
    </section>
  );
}
