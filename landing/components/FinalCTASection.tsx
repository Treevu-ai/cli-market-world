"use client";
import { useLang } from "@/lib/LanguageContext";
import { CTA } from "@/lib/ctaCopy";

export default function FinalCTASection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section
      id="final-cta"
      className="landing-section animate-fade-in scroll-mt-24"
      style={{ background: "linear-gradient(135deg, #fff7f0 0%, #fff5ed 50%, #fef3ea 100%)", borderTop: "1px solid #e2e8f0" }}
    >
      <div className="landing-container-wide text-center">
        <h2 className="section-title">
          {isES
            ? "Dale a tus agentes IA poder de compra real"
            : "Give your AI agents real buying power"}
        </h2>
        <p className="section-intro">
          {isES
            ? "Ve más allá de las recomendaciones. Busca, compara, aprueba y ejecuta comercio a través de una capa programable."
            : "Move beyond recommendations. Search, compare, approve, and execute commerce through one programmable layer."}
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <a
            href={CTA.getApiKey.href}
            className="inline-flex items-center rounded-[10px] bg-[#ea580c] text-[#f8fafc] text-base font-semibold px-8 py-3 hover:bg-[#f97316] active:bg-[#c2410c] transition-colors shadow-lg shadow-[#ea580c]/20"
          >
            {isES ? CTA.getApiKey.es : CTA.getApiKey.en}
          </a>
          <a
            href={CTA.bookDemo.href}
            className="inline-flex items-center rounded-[10px] border border-[#e2e8f0] text-[#0f172a] text-base font-semibold px-8 py-3 hover:border-[#ea580c] hover:text-[#ea580c] transition-colors"
          >
            {isES ? CTA.bookDemo.es : CTA.bookDemo.en}
          </a>
        </div>
      </div>
    </section>
  );
}
