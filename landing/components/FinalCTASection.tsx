"use client";
import { useLang } from "@/lib/LanguageContext";
import { PRICING_BUILD_HASH } from "@/lib/siteNav";

export default function FinalCTASection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section
      id="final-cta"
      className="landing-section animate-fade-in scroll-mt-24"
      style={{ background: "linear-gradient(135deg, #0d1a0a 0%, #111a0e 50%, #0a1a10 100%)", borderTop: "1px solid #27272A" }}
    >
      <div className="landing-container-wide text-center">
        <h2 className="section-title text-white">
          {isES
            ? "Dale a tus agentes IA poder de compra real"
            : "Give your AI agents real buying power"}
        </h2>
        <p className="section-intro" style={{ color: "rgba(255,255,255,0.8)" }}>
          {isES
            ? "Ve más allá de las recomendaciones. Busca, compara, aprueba y ejecuta comercio a través de una capa programable."
            : "Move beyond recommendations. Search, compare, approve, and execute commerce through one programmable layer."}
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <a
            href={PRICING_BUILD_HASH}
            className="inline-flex items-center rounded-[10px] bg-[#7CFF5B] text-[#09090B] text-base font-semibold px-8 py-3 hover:bg-[#8fff6e] active:bg-[#5be041] transition-colors shadow-lg shadow-[#7CFF5B]/20"
          >
            {isES ? "Obtener API Key →" : "Get API Key →"}
          </a>
          <a
            href="/contact"
            className="inline-flex items-center rounded-[10px] border border-[#27272A] text-[#FAFAFA] text-base font-semibold px-8 py-3 hover:border-[#7CFF5B] hover:text-[#7CFF5B] transition-colors"
          >
            {isES ? "Reservar Demo →" : "Book Demo →"}
          </a>
        </div>
      </div>
    </section>
  );
}
