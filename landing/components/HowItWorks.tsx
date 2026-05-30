"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

type Step = {
  cmd: string;
  out_es: string;
  out_en: string;
  label_es: string;
  label_en: string;
  icon: string;
  roadmap: boolean;
};

const steps: Step[] = [
  { cmd: "pip install cli-market", out_es: `cli-market ${MARKET_STATS.packageVersion} instalado`, out_en: `cli-market ${MARKET_STATS.packageVersion} installed`, label_es: "Install", label_en: "Install", icon: "↓", roadmap: false },
  { cmd: "market login", out_es: `Autenticado — ${MARKET_STATS.retailersVerified} retailers verificados listos`, out_en: `Authenticated — ${MARKET_STATS.retailersVerified} verified retailers ready`, label_es: "Login", label_en: "Login", icon: "🔑", roadmap: false },
  { cmd: "market search \"leche\" --country PE", out_es: "Wong S/4.20 · Metro S/3.90 · Plaza Vea S/4.50", out_en: "Wong S/4.20 · Metro S/3.90 · Plaza Vea S/4.50", label_es: "Search", label_en: "Search", icon: "🔍", roadmap: false },
  { cmd: "market compare \"arroz\"", out_es: "Mejor: Metro S/2.80 · Ahorro: S/0.70/unidad", out_en: "Best: Metro S/2.80 · Savings: S/0.70/unit", label_es: "Compare", label_en: "Compare", icon: "📊", roadmap: false },
  { cmd: "market add 1 --qty 2", out_es: "2x Leche Gloria → carrito", out_en: "2x Milk → cart", label_es: "Add · (en roadmap)", label_en: "Add · (roadmap)", icon: "🛒", roadmap: true },
  { cmd: "market checkout --payment yape", out_es: "QR generado · aprobación humana", out_en: "QR generated · human approval", label_es: "Checkout autónomo · (en roadmap)", label_en: "Autonomous checkout · (roadmap)", icon: "💳", roadmap: true },
];

export default function HowItWorks() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="how" className="landing-section landing-section-alt">
      <div className="landing-container-wide text-center">
        <p className="section-eyebrow mb-4">{isES ? "Cómo funciona" : "How it works"}</p>
        <h2 className="section-title mb-2">
          {isES ? "Del install a datos verificados en minutos." : "From install to verified data in minutes."}
        </h2>
        <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-xl mx-auto mb-8">
          {isES
            ? "Disponible hoy: Search → Compare → Export. En roadmap: Add y Checkout autónomo."
            : "Available today: Search → Compare → Export. On the roadmap: Add and autonomous Checkout."}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-left mb-10 min-w-0">
          {steps.map((s, i) => (
            <div
              key={i}
              className={`card-cyber header-strip px-5 py-4 flex items-start gap-3 min-w-0 overflow-hidden transition-all ${
                s.roadmap ? "opacity-75 border-dashed" : "hover:energy-border-active"
              }`}
            >
              <span className="text-lg shrink-0">{s.icon}</span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-bold text-white">{isES ? s.label_es : s.label_en}</p>
                <p className="text-xs text-[var(--cm-on-surface-variant)] font-mono mt-1 demo-step-text">{s.cmd}</p>
                <p className="text-[11px] text-[var(--cm-on-surface-variant)]/80 mt-1 demo-step-text">{isES ? s.out_es : s.out_en}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="mb-8">
          <img
            src="/demo.gif"
            alt={isES ? "Demo: agente de IA comprando canasta básica en supermercados peruanos con CLI Market" : "Demo: AI agent shopping a basic basket at Peruvian supermarkets with CLI Market"}
            className="mx-auto rounded-xl border border-[var(--cm-outline-variant)]/40 shadow-2xl max-w-full h-auto energy-border"
            width={960}
            height={540}
          />
          <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-2 font-mono">
            {isES
              ? "Agente IA · canasta básica PE · 30 verificados · comparación en ~14 s (el pago aún requiere aprobación humana)."
              : "AI agent · PE basic basket · 30 verified · comparison in ~14 s (payment still requires human approval)."}
          </p>
        </div>

        <a href="https://pypi.org/project/cli-market/" className="btn-mint cyber-glow-mint">
          {isES ? "Empezar gratis con la API →" : "Start free with the API →"}
        </a>
      </div>
    </section>
  );
}
