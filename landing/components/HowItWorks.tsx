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
    <section id="how" className="relative bg-[var(--wise-canvas-soft)] py-24 border-t border-[var(--wise-green-pale)]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-8">
          {isES ? "Cómo funciona" : "How it works"}
        </p>
        <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-3 tracking-tight">
          {isES ? "Del install a la compra en menos de 1 minuto." : "From install to purchase in under 1 minute."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-md mx-auto mb-12">
          {isES ? "Una CLI. Un flujo. Sin fricción." : "One CLI. One flow. Zero friction."}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
          {steps.map((s, i) => (
            <div key={i} className="bg-[var(--wise-canvas)] rounded-3xl border border-[var(--wise-green-pale)] p-4 flex items-start gap-4">
              <span className="text-xl shrink-0">{s.icon}</span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-bold text-[var(--wise-ink)]">{s.label}</p>
                <p className="text-xs text-[var(--wise-mute)] font-mono mt-1 truncate">{s.cmd}</p>
                <p className="text-[11px] text-[var(--wise-body)] mt-1 truncate">{isES ? s.out_es : s.out_en}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
