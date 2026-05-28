"use client";
import { useLang } from "@/lib/LanguageContext";

export default function Hero() {
  const { t: _t, lang } = useLang();
  const isES = lang === "es";

  const chips = [
    { num: "30", label: isES ? "comercios" : "retailers" },
    { num: "7", label: isES ? "países" : "countries" },
    { num: "13K", label: isES ? "precios reales" : "real prices" },
    { num: "8h", label: isES ? "actualización" : "refresh cycle" },
  ];

  return (
    <section className="relative min-h-screen flex flex-col bg-[var(--wise-canvas-soft)]">
      <div className="flex-1 flex flex-col justify-center items-center px-6 py-32 lg:py-40 text-center">
        <h1 className="text-[clamp(36px,7vw,72px)] leading-[0.95] font-black text-[var(--wise-ink)] max-w-[720px] tracking-tight">
          {isES
            ? "La economía agentiva ya empezó.\nTu negocio, adentro o afuera."
            : "The agent economy is here.\nIs your business inside or out."}
        </h1>

        <p className="mt-4 text-base sm:text-lg text-[var(--wise-body)] max-w-[500px] leading-relaxed">
          {isES
            ? "Los agentes de IA ya buscan, comparan y compran productos sin intervención humana. CLI Market es el índice donde te encuentran. Si no estás aquí, no existes para ellos."
            : "AI agents already search, compare, and buy products without human input. CLI Market is the index where they find you. If you're not here, you don't exist to them."}
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
          {chips.map((c) => (
            <span key={c.label} className="inline-flex items-center gap-1.5 bg-[var(--wise-canvas)] rounded-3xl px-4 py-2 text-sm border border-[var(--wise-green-pale)]">
              <strong className="text-[var(--wise-ink)]">{c.num}</strong>
              <span className="text-[var(--wise-mute)]">{c.label}</span>
            </span>
          ))}
          <span className="inline-flex items-center gap-1 bg-[var(--wise-green-pale)] rounded-3xl px-4 py-2 text-sm">
            <span className="text-[var(--wise-ink)] font-semibold">{isES ? "GRATIS" : "FREE"}</span>
          </span>
        </div>

        <div className="mt-10 flex flex-col sm:flex-row items-center gap-3">
          <a href="#retailers"
             className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 hover:bg-[var(--wise-green-hover)] transition-colors shadow-sm">
            {isES ? "Agregar mi tienda →" : "List my store →"}
          </a>
          <button
            onClick={(e) => {
              navigator.clipboard.writeText("pip install cli-market && market login");
              const btn = e.currentTarget;
              const orig = btn.innerHTML;
              btn.innerHTML = isES ? "Copiado" : "Copied";
              btn.classList.add("pointer-events-none");
              setTimeout(() => { btn.innerHTML = orig; btn.classList.remove("pointer-events-none"); }, 1800);
            }}
            className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-canvas)] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 border-2 border-[var(--wise-green-pale)] hover:border-[var(--wise-green)] transition-colors cursor-pointer">
            {isES ? "Para developers" : "For developers"}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          </button>
        </div>
      </div>

      <div className="pb-10 flex justify-center">
        <div className="inline-flex items-center gap-2 bg-[var(--wise-canvas)] rounded-3xl px-5 py-3 shadow-sm border border-[var(--wise-green-pale)]">
          <span className="w-3 h-3 rounded-full bg-[#d03238]" />
          <span className="w-3 h-3 rounded-full bg-[#ffd11a]" />
          <span className="w-3 h-3 rounded-full bg-[#2ead4b]" />
          <code className="font-mono text-sm text-[var(--wise-body)] ml-3">pip install cli-market</code>
        </div>
      </div>
    </section>
  );
}
