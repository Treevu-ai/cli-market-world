"use client";

import { useLang } from "@/lib/LanguageContext";

type AdvisorPack = {
  id: "a" | "b" | "c";
  name_es: string;
  name_en: string;
  priceUsd: number;
  period_es: string;
  period_en: string;
  features_es: string[];
  features_en: string[];
  featured?: boolean;
  cta_es: string;
  cta_en: string;
};

const PACKS: AdvisorPack[] = [
  {
    id: "a",
    name_es: "Pack A — Brief",
    name_en: "Pack A — Brief",
    priceUsd: 49,
    period_es: "pago único",
    period_en: "one-time",
    features_es: [
      "1 categoría + 1 país",
      "Comparativa de 3–5 referencias",
      "Rango de precio + recomendación de canal",
      "Entrega en 48h",
    ],
    features_en: [
      "1 category + 1 country",
      "3–5 reference-brand comparison",
      "Price range + channel recommendation",
      "Delivered in 48h",
    ],
    cta_es: "Pedir un Brief",
    cta_en: "Request a Brief",
  },
  {
    id: "b",
    name_es: "Pack B — Sesión",
    name_en: "Pack B — Session",
    priceUsd: 149,
    period_es: "pago único",
    period_en: "one-time",
    features_es: [
      "Sesión asistida en vivo (60 min)",
      "Operamos la consola juntos",
      "Resolvemos hipótesis de precio y plaza",
      "Incluye 1 Brief",
    ],
    features_en: [
      "Live assisted session (60 min)",
      "We run the console together",
      "Resolve pricing and channel hypotheses",
      "Includes 1 Brief",
    ],
    featured: true,
    cta_es: "Agendar sesión",
    cta_en: "Book a session",
  },
  {
    id: "c",
    name_es: "Pack C — Retainer",
    name_en: "Pack C — Retainer",
    priceUsd: 300,
    period_es: "/ mes",
    period_en: "/ mo",
    features_es: [
      "Brief ejecutivo recurrente (semanal o mensual)",
      "Radar de señales y anomalías",
      "Historial y alertas de inflación",
      "Canal directo con el equipo",
    ],
    features_en: [
      "Recurring executive brief (weekly or monthly)",
      "Signal and anomaly radar",
      "Inflation history and alerts",
      "Direct channel with our team",
    ],
    cta_es: "Solicitar retainer",
    cta_en: "Request retainer",
  },
];

function PackCard({ pack, isES }: { pack: AdvisorPack; isES: boolean }) {
  const features = isES ? pack.features_es : pack.features_en;

  return (
    <div
      className={`relative h-full rounded-2xl p-6 text-left flex flex-col ${pack.featured ? "energy-border-active card-cyber" : "card-cyber"}`}
      style={pack.featured ? { background: "var(--cm-mint)", borderColor: "var(--cm-mint)" } : undefined}
    >
      {pack.featured && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--cm-ink)] text-[var(--cm-background)] text-xs font-semibold px-4 py-1 rounded-full whitespace-nowrap shadow-sm">
          {isES ? "Recomendado" : "Recommended"}
        </span>
      )}

      <h3 className={`text-lg font-bold ${pack.featured ? "text-[var(--cm-on-mint)]" : "text-[var(--cm-on-surface)]"}`}>
        {isES ? pack.name_es : pack.name_en}
      </h3>

      <div className="mt-3 mb-1 flex flex-wrap items-baseline gap-x-2">
        <span className={`text-3xl font-black tabular-nums ${pack.featured ? "text-[var(--cm-on-mint)]" : "text-[var(--cm-on-surface)]"}`}>
          ${pack.priceUsd}
        </span>
        <span className={`text-sm ${pack.featured ? "text-[var(--cm-on-mint)]/85" : "text-[var(--cm-on-surface-variant)]"}`}>
          {isES ? pack.period_es : pack.period_en}
        </span>
      </div>

      <ul className="space-y-3 mb-6 mt-4 flex-1">
        {features.map((f) => (
          <li
            key={f}
            className={`flex items-start gap-2.5 text-sm leading-relaxed ${pack.featured ? "text-[var(--cm-on-mint)]/90" : "text-[var(--cm-on-surface-variant)]"}`}
          >
            <svg
              className="w-4 h-4 mt-0.5 shrink-0"
              viewBox="0 0 24 24"
              fill="none"
              stroke={pack.featured ? "var(--cm-on-mint)" : "var(--cm-mint)"}
              strokeWidth="2.5"
            >
              <path d="M20 6L9 17l-5-5" />
            </svg>
            {f}
          </li>
        ))}
      </ul>

      <a href="#contact-form" className={`mt-auto ${pack.featured ? "btn-mint w-full" : "btn-outline w-full"}`}>
        {isES ? pack.cta_es : pack.cta_en}
      </a>
    </div>
  );
}

export default function AdvisorPricingSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="advisor-pricing" className="landing-section landing-section-alt scroll-mt-24">
      <div className="landing-container-wide">
        <div className="landing-section-header text-center">
          <p className="section-eyebrow mb-4">{isES ? "PLANES" : "PLANS"}</p>
          <h2 className="section-title">{isES ? "Elige tu punto de entrada" : "Pick your entry point"}</h2>
          <p className="section-intro">
            {isES
              ? "Del piloto puntual al retainer recurrente — mismo respaldo de datos, distinto compromiso."
              : "From a one-off pilot to a recurring retainer — same data backing, different commitment."}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mt-10 max-w-4xl mx-auto">
          {PACKS.map((pack) => (
            <PackCard key={pack.id} pack={pack} isES={isES} />
          ))}
        </div>
      </div>
    </section>
  );
}
