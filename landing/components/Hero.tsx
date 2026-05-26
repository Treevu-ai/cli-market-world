"use client";
import { useLang } from "@/lib/LanguageContext";

export default function Hero() {
  const { t: _t, lang } = useLang();
  const isES = lang === "es";

  return (
    <section className="relative min-h-screen flex flex-col bg-[var(--wise-canvas-soft)]">
      <div className="flex-1 flex flex-col justify-center items-center px-6 py-24 lg:py-32 text-center">
        <h1 className="text-[clamp(40px,7vw,80px)] leading-[0.92] font-black text-[var(--wise-ink)] max-w-[760px] tracking-tight">
          {isES
            ? "Infraestructura de comercio y precios para agentes de IA."
            : "Commerce and pricing infrastructure for AI agents."}
        </h1>

        <p className="mt-5 text-lg text-[var(--wise-body)] max-w-[520px] leading-relaxed">
          {isES
            ? "Para equipos de data, fintechs y builders de agentes que necesitan precios reales y checkout en LatAm y Europa."
            : "For data teams, fintechs, and agent builders who need real shelf prices and checkout across LatAm and Europe."}
        </p>

        <p className="mt-4 text-sm text-[var(--wise-mute)] max-w-[480px]">
          {isES
            ? "60 retailers · 11 países · 3 plataformas · 36 MCP tools · MIT License · Sin scraping."
            : "60 retailers · 11 countries · 3 platforms · 36 MCP tools · MIT · No scraping."}
        </p>

        <div className="mt-8 flex flex-col sm:flex-row items-center gap-3">
          <button
            onClick={() => { navigator.clipboard.writeText("pip install cli-market && market login"); }}
            className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 hover:bg-[var(--wise-green-hover)] transition-colors cursor-pointer">
            {isES ? "Instalar CLI" : "Install CLI"}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          </button>
          <a href="#api"
             className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-canvas)] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 border border-[var(--wise-green-pale)] hover:bg-[var(--wise-green-pale)] transition-colors">
            {isES ? "Ver API" : "View API"}
          </a>
        </div>
      </div>

      <div className="pb-12 flex justify-center">
        <div className="inline-flex items-center gap-2 bg-[var(--wise-canvas)] rounded-3xl px-5 py-3 shadow-sm">
          <span className="w-3 h-3 rounded-full bg-[#d03238]" />
          <span className="w-3 h-3 rounded-full bg-[#ffd11a]" />
          <span className="w-3 h-3 rounded-full bg-[#2ead4b]" />
          <code className="font-mono text-sm text-[var(--wise-body)] ml-3">pip install cli-market</code>
        </div>
      </div>
    </section>
  );
}
