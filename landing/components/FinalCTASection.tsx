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
      style={{ background: "linear-gradient(135deg, #533afd 0%, #3b82f6 100%)" }}
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
            className="inline-flex items-center rounded-full bg-white text-[#533afd] text-base font-semibold px-8 py-3 hover:bg-gray-100 active:bg-gray-200 transition-colors shadow-sm"
          >
            {isES ? "Obtener API Key →" : "Get API Key →"}
          </a>
          <a
            href="/contact"
            className="inline-flex items-center rounded-full border-2 border-white text-white text-base font-semibold px-8 py-3 hover:bg-white/10 transition-colors"
          >
            {isES ? "Reservar Demo →" : "Book Demo →"}
          </a>
        </div>
      </div>
    </section>
  );
}
