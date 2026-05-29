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
    <section id="how" className="relative bg-[var(--wise-ink)] py-16">
      <div className="landing-container px-6 text-center">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-4">
          {isES ? "Cómo funciona" : "How it works"}
        </p>
        <h2 className="text-[clamp(22px,4vw,28px)] font-medium text-white mb-2 tracking-tight">
          {isES ? "Del install a la compra en menos de 1 minuto." : "From install to purchase in under 1 minute."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-xl mx-auto mb-8">
          {isES ? "Search → Compare → Cart → Checkout. Demo en vivo abajo." : "Search → Compare → Cart → Checkout. Live demo below."}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-left mb-10">
          {steps.map((s, i) => (
            <div key={i} className="bg-[#1a1d19] rounded-2xl border border-[#2a2d25] p-4 flex items-start gap-3">
              <span className="text-lg shrink-0">{s.icon}</span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-bold text-white">{s.label}</p>
                <p className="text-xs text-[var(--wise-mute)] font-mono mt-1 truncate">{s.cmd}</p>
                <p className="text-[11px] text-[var(--wise-body)] mt-1 truncate">{isES ? s.out_es : s.out_en}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="mb-8">
          <img
            src="/demo.gif"
            alt={isES ? "Demo: agente de IA comprando canasta básica en supermercados peruanos con CLI Market" : "Demo: AI agent shopping a basic basket at Peruvian supermarkets with CLI Market"}
            className="mx-auto rounded-xl border border-[#2a2d25] shadow-lg max-w-full h-auto"
            width={960}
            height={540}
          />
          <p className="text-[10px] text-[var(--wise-mute)] mt-2 font-mono">
            {isES ? "Agente IA · canasta básica PE · 9 supermercados · 14 s" : "AI agent · PE basic basket · 9 supermarkets · 14 s"}
          </p>
        </div>

        <a
          href="https://pypi.org/project/cli-market/"
          className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 hover:bg-[var(--wise-green-hover)] transition-colors"
        >
          {isES ? "Instalar gratis →" : "Install free →"}
        </a>
      </div>
    </section>
  );
}
