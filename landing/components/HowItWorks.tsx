"use client";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { recordPipInstallIntent } from "@/lib/funnel";

const steps = [
  {
    cmd: MARKET_STATS.pipInstallCmd,
    out_es: `${MARKET_STATS.pypiPackageName} ${MARKET_STATS.packageVersion} · MIT`,
    out_en: `${MARKET_STATS.pypiPackageName} ${MARKET_STATS.packageVersion} · MIT`,
    label: "Install",
    icon: "↓",
  },
  {
    cmd: "market init",
    out_es: `Cuenta free · ${MARKET_STATS.retailersVerified} retailers · ${MARKET_STATS.mcpTools} MCP`,
    out_en: `Free account · ${MARKET_STATS.retailersVerified} retailers · ${MARKET_STATS.mcpTools} MCP`,
    label: "Init",
    icon: "⚡",
  },
  {
    cmd: "market discover --country PE",
    out_es: "Shop bundle · retailers + líneas + países en una llamada",
    out_en: "Shop bundle · retailers + lines + countries in one call",
    label: "Discover",
    icon: "🛒",
  },
  {
    cmd: 'market compare "arroz" --country PE',
    out_es: "Metro S/2.90 · Wong S/3.10 · precio/kg normalizado",
    out_en: "Metro S/2.90 · Wong S/3.10 · normalized per kg",
    label: "Compare",
    icon: "🔍",
  },
  {
    cmd: 'market basket "arroz:1 leche:1" --country PE',
    out_es: "Canasta multi-retailer · mejor total en <1s",
    out_en: "Multi-retailer basket · best total in <1s",
    label: "Basket",
    icon: "🧺",
  },
  {
    cmd: "market tools",
    out_es: `Shop · Intel · Account · ${MARKET_STATS.mcpTools} tools (46 legacy)`,
    out_en: `Shop · Intel · Account · ${MARKET_STATS.mcpTools} tools (46 legacy)`,
    label: "MCP",
    icon: "🔌",
  },
];

export default function HowItWorks() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="how" className="landing-section landing-section-alt animate-fade-in">
      <div className="landing-container text-center">
        <p className="section-eyebrow mb-4 mt-2">
          {isES ? "Cómo funciona" : "How it works"}
        </p>
        <h2 className="section-title">
          {isES ? "Del install a datos verificados en minutos." : "From install to verified data in minutes."}
        </h2>
        <p className="section-intro max-w-xl">
          {isES
            ? `Init → Discover → Compare → Basket → MCP. ${MARKET_STATS.mcpTools} herramientas, bundles Shop/Intel/Account, checkout Pro.`
            : `Init → Discover → Compare → Basket → MCP. ${MARKET_STATS.mcpTools} tools, Shop/Intel/Account bundles, Pro checkout.`}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 text-left mb-12 min-w-0">
          {steps.map((s, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="card-cyber px-5 py-5 flex items-start gap-4 min-w-0 overflow-hidden"
              onClick={i === 0 ? () => recordPipInstallIntent("landing_how_install") : undefined}
              role={i === 0 ? "button" : undefined}
              tabIndex={i === 0 ? 0 : undefined}
              onKeyDown={
                i === 0
                  ? (e) => {
                      if (e.key === "Enter" || e.key === " ") recordPipInstallIntent("landing_how_install");
                    }
                  : undefined
              }
            >
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
          {isES ? `Checkout ${MARKET_STATS.paymentsLabel} · requiere plan Pro + activación por email` : `Checkout via ${MARKET_STATS.paymentsLabel} · requires Pro plan + email activation`}
        </p>

        <p className="mt-8">
          <a href="/docs#quickstart" className="font-mono text-xs underline underline-offset-2 decoration-[var(--cm-mint)]/30 text-[var(--cm-mint)]/70 hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Demo completa de 8 pasos →" : "Full 8-step walkthrough →"}
          </a>
        </p>
      </div>
    </section>
  );
}