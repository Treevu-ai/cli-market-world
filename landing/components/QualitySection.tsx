"use client";
import { useLang } from "@/lib/LanguageContext";

export default function QualitySection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const bullets = isES
    ? [
        "Normalización por kilo y por litro — compara 900 ml, 1 L y 1,5 L con justicia.",
        "Filtro de descuentos imposibles y brechas anómalas antes de publicar spreads.",
        "Canasta básica con matcher de producto + packs estándar (AR, PE, BR y más).",
        "Dashboard en vivo con capas inventario / frescura / calidad para tu equipo.",
      ]
    : [
        "Per-kg and per-liter normalization — fair compare across pack sizes.",
        "Impossible discounts and outlier spreads filtered before public metrics.",
        "Standard basket matching with product + pack rules (AR, PE, BR, and more).",
        "Live dashboard with inventory / freshness / quality layers for your team.",
      ];

  return (
    <section id="quality" className="relative bg-[var(--wise-canvas-soft)] py-16 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-4">
          {isES ? "Calidad del dato" : "Data quality"}
        </p>
        <h2 className="text-[22px] font-medium text-[var(--wise-ink)] mb-3 tracking-tight">
          {isES
            ? "Precios de góndola reales, listos para agentes."
            : "Real shelf prices, agent-ready."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-lg mx-auto mb-8">
          {isES
            ? "Cada precio pasa controles antes de alimentar comparaciones y copy público. Tu agente no recibe un -99% mal leído como si fuera oferta."
            : "Prices are checked before they power comparisons and public metrics. Your agent won't treat a scraped -99% as a real deal."}
        </p>
        <ul className="text-left max-w-md mx-auto space-y-3 text-sm text-[var(--wise-body)]">
          {bullets.map((b) => (
            <li key={b} className="flex gap-2">
              <span className="text-[var(--wise-green)] shrink-0">→</span>
              <span>{b}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
