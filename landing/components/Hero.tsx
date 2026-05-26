"use client";
import { useLang } from "@/lib/LanguageContext";

export default function Hero() {
  const { t: _t, lang } = useLang();
  const isES = lang === "es";

  return (
    <section className="relative min-h-screen flex flex-col bg-[var(--wise-canvas-soft)]">
      <div className="flex-1 flex flex-col justify-center items-center px-6 py-24 lg:py-32 text-center">
        <h1 className="text-[clamp(40px,7vw,96px)] leading-[0.88] font-black text-[var(--wise-ink)] max-w-[800px] tracking-tight">
          {_t("hero_h1")}
        </h1>
        <p className="mt-6 text-lg text-[var(--wise-body)] max-w-[480px] leading-relaxed">
          {_t("hero_sub")}
        </p>
        <div className="mt-10 flex flex-col sm:flex-row items-center gap-3">
          <a href="https://github.com/Treevu-ai/cli-market-world"
             className="inline-flex items-center gap-2 rounded-3xl bg-[#9fe870] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 hover:bg-[#cdffad] transition-colors">
            {_t("hero_install")}
            <span className="opacity-60">→</span>
          </a>
          <a href="#api"
             className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-green-pale)] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 hover:bg-[#c5edab] transition-colors">
            {_t("hero_cov")}
          </a>
        </div>
        <div className="mt-16 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-[var(--wise-body)] font-medium">
          <span><strong className="text-[var(--wise-ink)] text-lg">60</strong> {isES ? "comercios" : "retailers"}</span>
          <span className="text-[#c5edab] hidden sm:inline">·</span>
          <span><strong className="text-[var(--wise-ink)] text-lg">11</strong> {isES ? "países" : "countries"}</span>
          <span className="text-[#c5edab] hidden sm:inline">·</span>
          <span><strong className="text-[var(--wise-ink)] text-lg">36</strong> {isES ? "herramientas MCP" : "MCP tools"}</span>
          <span className="text-[#c5edab] hidden sm:inline">·</span>
          <span><strong className="text-[var(--wise-ink)] text-lg">3</strong> {isES ? "plataformas" : "platforms"}</span>
        </div>
      </div>
      <div className="pb-12 flex justify-center">
        <div className="inline-flex items-center gap-2 bg-white rounded-3xl px-5 py-3 shadow-sm">
          <span className="w-3 h-3 rounded-full bg-[#d03238]" />
          <span className="w-3 h-3 rounded-full bg-[#ffd11a]" />
          <span className="w-3 h-3 rounded-full bg-[#2ead4b]" />
          <code className="font-mono text-sm text-[var(--wise-body)] ml-3">pip install cli-market</code>
          <button onClick={() => navigator.clipboard.writeText("pip install cli-market")}
            className="ml-2 text-[var(--wise-body)] hover:text-[var(--wise-ink)] transition-colors" title="Copiar">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          </button>
        </div>
      </div>
    </section>
  );
}
