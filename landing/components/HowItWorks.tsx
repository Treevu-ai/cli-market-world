"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const steps = [
  { cmd: "pip install cli-market", out_es: `cli-market ${MARKET_STATS.packageVersion} instalado`, out_en: `cli-market ${MARKET_STATS.packageVersion} installed`, label: "Install", icon: "↓" },
  { cmd: "market login", out_es: `Autenticado — ${MARKET_STATS.retailersVerified} retailers verificados listos`, out_en: `Authenticated — ${MARKET_STATS.retailersVerified} verified retailers ready`, label: "Login", icon: "🔑" },
  { cmd: "market search \"leche\" --country PE", out_es: "Wong S/4.20 · Metro S/3.90 · Plaza Vea S/4.50", out_en: "Wong S/4.20 · Metro S/3.90 · Plaza Vea S/4.50", label: "Search", icon: "🔍" },
  { cmd: "market compare \"arroz\"", out_es: "Mejor: Metro S/2.80 · Ahorro: S/0.70/unidad", out_en: "Best: Metro S/2.80 · Savings: S/0.70/unit", label: "Compare", icon: "📊" },
  { cmd: "market add 1 --qty 2", out_es: "2x Leche Gloria → carrito", out_en: "2x Milk → cart", label: "Add", icon: "🛒" },
  { cmd: "market checkout --payment yape", out_es: "✓ Orden confirmada · QR generado", out_en: "✓ Order confirmed · QR generated", label: "Checkout", icon: "💳" },
];

export default function HowItWorks() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="how" className="landing-section-alt animate-fade-in">
      <div className="landing-container text-center">
        <p className="section-eyebrow mb-4">
          {isES ? "Cómo funciona" : "How it works"}
        </p>
        <h2 className="section-title mb-2">
          {isES ? "Del install a datos verificados en minutos." : "From install to verified data in minutes."}
        </h2>
        <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-xl mx-auto mb-8">
          {isES
            ? "Search → Compare → export. Foco comercial: Intelligence (spreads, inflación, canasta)."
            : "Search → Compare → export. Commercial focus: Intelligence (spreads, inflation, basket)."}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-left mb-10 min-w-0">
          {steps.map((s, i) => (
            <div key={i} className="card-cyber px-5 py-4 flex items-start gap-3 min-w-0 overflow-hidden">
              <span className="text-lg shrink-0">{s.icon}</span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-bold text-white">{s.label}</p>
                <p className="text-xs text-[var(--cm-on-surface-variant)] font-mono mt-1 demo-step-text">{s.cmd}</p>
                <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-1 demo-step-text">{isES ? s.out_es : s.out_en}</p>
              </div>
            </div>
          ))}
        </div>

        <a
          href="https://pypi.org/project/cli-market/"
          className="btn-mint"
        >
          {isES ? "Empezar con la API — gratis →" : "Start with the API — free →"}
        </a>
      </div>
    </section>
  );
}
