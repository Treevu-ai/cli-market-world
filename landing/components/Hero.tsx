"use client";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import ScrambleText from "@/components/ScrambleText";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLiveStats } from "@/hooks/useLiveStats";
import { recordPipInstallIntent } from "@/lib/funnel";

export default function Hero() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { pypiChip } = useLiveStats();
  return (
    <section id="hero" className="landing-section animate-fade-in relative min-h-0 md:min-h-[90vh] flex flex-col overflow-hidden">
      {/* Aura glow behind title */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[min(100vw,600px)] h-[min(100vw,600px)] rounded-full bg-[var(--cm-mint)]/5 blur-[80px] md:blur-[120px]" />
        <div className="hidden sm:block absolute top-1/2 left-1/3 w-[400px] h-[400px] rounded-full bg-[var(--cm-mint)]/8 blur-[100px]" />
      </div>


      <div className="flex-1 flex flex-col justify-center items-center landing-container pt-16 pb-16 sm:pt-20 sm:pb-20 lg:pt-28 lg:pb-32 text-center min-w-0 relative z-10">
        <motion.h1 initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease: "easeOut" }} className="text-[clamp(28px,7.5vw,64px)] leading-[1.05] font-black text-white max-w-[900px] tracking-tight text-balance">
          {isES
            ? "La capa programable del retail físico de LatAm."
            : "The programmable layer for physical retail in LatAm."}
        </motion.h1>

        <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.15, ease: "easeOut" }} className="section-intro mt-6 max-w-[640px]">
          {isES
            ? `Una API sobre ${MARKET_STATS.retailersDefined} retailers en ${MARKET_STATS.countries} países. ${MARKET_STATS.mcpTools} herramientas MCP y precios de góndola normalizados por kg/L.`
            : `One API across ${MARKET_STATS.retailersDefined} retailers in ${MARKET_STATS.countries} countries. ${MARKET_STATS.mcpTools} MCP tools and shelf prices normalized per kg/L.`}
          {" "}
          <a href="#coverage" className="text-[var(--cm-mint)] underline underline-offset-2 hover:brightness-110">
            {isES ? "Ver cobertura →" : "See coverage →"}
          </a>
        </motion.p>

        <div className="mt-8 sm:mt-10 grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 w-full max-w-[960px] mx-auto">
          <a
            href={MARKET_STATS.pypiUrl}
            onClick={() => recordPipInstallIntent("landing_hero")}
            className="group flex flex-col items-center gap-2 rounded-2xl bg-[var(--cm-mint)] text-[var(--cm-on-mint)] px-6 py-5 hover:brightness-110 hover:scale-[1.02] transition-all duration-200 text-left sm:items-start"
          >
            <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-on-mint)]/70">
              {isES ? "Para builders / agentes" : "For builders / agents"}
            </span>
            <span className="text-base font-semibold">
              <ScrambleText text={isES ? "Empezar con la API — gratis →" : "Start with the API — free →"} />
            </span>
            <code className="font-mono text-xs text-[var(--cm-on-mint)]/80">{MARKET_STATS.pipInstallCmd}</code>
            <img
              src={MARKET_STATS.pepyBadgeUrl}
              alt={isES ? "Descargas PyPI (Pepy.tech)" : "PyPI downloads (Pepy.tech)"}
              width={180}
              height={20}
              loading="lazy"
              className="h-5 w-auto max-w-full opacity-90 group-hover:opacity-100 transition-opacity"
            />
            {pypiChip ? (
              <span className="text-[10px] font-mono text-[var(--cm-on-mint)]/65">
                {pypiChip} {isES ? "instalaciones PyPI" : "PyPI installs"}
              </span>
            ) : null}
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
          <a
            href="#intelligence"
            className="group flex flex-col items-center gap-2 rounded-2xl border border-[var(--cm-outline-variant)]/40 bg-transparent px-6 py-5 hover:bg-white/5 hover:scale-[1.02] transition-all duration-200 text-left sm:items-start"
          >
            <span className="text-xs font-mono uppercase tracking-widest text-[var(--cm-on-surface-variant)]">
              {isES ? "Intelligence" : "Intelligence"}
            </span>
            <span className="text-base font-semibold text-white">
              {isES ? "Datos para equipos comerciales →" : "Data for commercial teams →"}
            </span>
            <span className="text-xs text-[var(--cm-on-surface-variant)]">
              {isES ? "Lista de espera · gratis" : "Waitlist · free"}
            </span>
          </a>
        </div>

        <div className="mt-12 w-full max-w-[900px]">
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
