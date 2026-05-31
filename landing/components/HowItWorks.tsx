"use client";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const steps = [
  { cmd: "pip install cli-market", out_es: `cli-market ${MARKET_STATS.packageVersion} instalado`, out_en: `cli-market ${MARKET_STATS.packageVersion} installed`, label: "Install", icon: "↓" },
  { cmd: "market hello", out_es: `${MARKET_STATS.retailersDefined} retailers · ${MARKET_STATS.pricesVerifiedLabel} precios · ${MARKET_STATS.mcpTools} MCP tools`, out_en: `${MARKET_STATS.retailersDefined} retailers · ${MARKET_STATS.pricesVerifiedLabel} prices · ${MARKET_STATS.mcpTools} MCP tools`, label: "Hello", icon: "👋" },
  { cmd: "market search \"leche\" --country PE", out_es: "Wong S/4.20 · Metro S/3.90 · Plaza Vea S/4.50", out_en: "Wong S/4.20 · Metro S/3.90 · Plaza Vea S/4.50", label: "Search", icon: "🔍" },
  { cmd: "market indicators --country PE", out_es: `${MARKET_STATS.indicatorsCount} indicadores · OFF · Wikimedia · World Bank · IMF`, out_en: `${MARKET_STATS.indicatorsCount} indicators · OFF · Wikimedia · World Bank · IMF`, label: "Indicators", icon: "📊" },
  { cmd: "market ask \"compra arroz al mejor precio\"", out_es: "Metro S/2.80 · Ahorro: S/0.70/unidad", out_en: "Best: Metro S/2.80 · Savings: S/0.70/unit", label: "Ask", icon: "💬" },
  { cmd: "market basket \"arroz:1 aceite:1 leche:1\" --country AR", out_es: "Carrefour $3.20 · Jumbo $3.50 · Vea $2.90", out_en: "Carrefour $3.20 · Jumbo $3.50 · Vea $2.90", label: "Basket", icon: "🧺" },
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
            ? `Hello → Search → Indicators → Ask → Basket. ${MARKET_STATS.mcpTools} herramientas MCP, ${MARKET_STATS.indicatorsCount} indicadores, checkout Pro.`
            : `Hello → Search → Indicators → Ask → Basket. ${MARKET_STATS.mcpTools} MCP tools, ${MARKET_STATS.indicatorsCount} indicators, Pro checkout.`}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-left mb-10 min-w-0">
          {steps.map((s, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: i * 0.08 }} className="card-cyber px-5 py-4 flex items-start gap-3 min-w-0 overflow-hidden">
              <span className="text-lg shrink-0">{s.icon}</span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-bold text-white">{s.label}</p>
                <p className="text-xs text-[var(--cm-on-surface-variant)] font-mono mt-1 demo-step-text">{s.cmd}</p>
                <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-1 demo-step-text">{isES ? s.out_es : s.out_en}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mb-6 font-mono">
          {isES ? "Checkout con PayPal o QR (Yape/Plin) · requiere plan Pro + activación por email" : "Checkout via PayPal or QR (Yape/Plin) · requires Pro plan + email activation"}
        </p>

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
