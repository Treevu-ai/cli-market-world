"use client";
import { useLang } from "@/lib/LanguageContext";

const cases = [
  {
    icon: "🤖",
    title_es: "Agentes de compra",
    title_en: "Shopping agents",
    desc_es: "Search, compare, cart y checkout autónomo con 36 herramientas MCP.",
    desc_en: "Autonomous search, compare, cart, and checkout with 36 MCP tools.",
  },
  {
    icon: "📊",
    title_es: "Pricing & market intelligence",
    title_en: "Pricing & market intelligence",
    desc_es: "43K+ precios de góndola normalizados por kg/L, refresco cada 8h, export JSON/CSV.",
    desc_en: "43K+ shelf prices normalized per kg/L, 8h refresh, JSON/CSV export.",
  },
  {
    icon: "💳",
    title_es: "Fintech & pagos",
    title_en: "Fintech & payments",
    desc_es: "Checkout programático con QR (Yape/Plin/PayPal) y confirmación por webhook.",
    desc_en: "Programmatic checkout with QR (Yape/Plin/PayPal) and webhook confirmation.",
  },
  {
    icon: "🏛",
    title_es: "Bureaus & competitive intelligence",
    title_en: "Bureaus & competitive intelligence",
    desc_es: "Datos multi-retailer y multi-país por una sola API, listos para enriquecer tus reportes.",
    desc_en: "Multi-retailer, multi-country data through one API — ready to enrich your reports.",
  },
];

export default function UseCasesSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="casos" className="relative bg-[var(--wise-canvas-soft)] py-16 border-t border-[#c5edab]">
      <div className="landing-container text-center">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-4">
          {isES ? "Casos de uso" : "Use cases"}
        </p>
        <h2 className="text-[clamp(22px,4vw,28px)] font-medium text-[var(--wise-ink)] mb-2 tracking-tight">
          {isES ? "Una API. Muchas cosas encima." : "One API. Many things on top."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-xl mx-auto mb-10">
          {isES
            ? "Fintechs, analysts, bureaus y agentes — un solo punto de integración."
            : "Fintechs, analysts, bureaus, and agents — one integration point."}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-[800px] mx-auto text-left mb-10">
          {cases.map((c) => (
            <div
              key={c.title_es}
              className="bg-[var(--wise-canvas)] border border-[var(--wise-green-pale)] rounded-2xl p-6 flex flex-col gap-3"
            >
              <span className="text-2xl" aria-hidden="true">{c.icon}</span>
              <h3 className="text-sm font-bold text-[var(--wise-ink)]">
                {isES ? c.title_es : c.title_en}
              </h3>
              <p className="text-sm text-[var(--wise-body)] leading-relaxed">
                {isES ? c.desc_es : c.desc_en}
              </p>
            </div>
          ))}
        </div>

        <a
          href="#api"
          className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-ink)] text-[var(--wise-canvas)] text-sm font-semibold px-8 py-3 hover:opacity-90 transition-opacity"
        >
          {isES ? "Ver la API →" : "View the API →"}
        </a>
      </div>
    </section>
  );
}
