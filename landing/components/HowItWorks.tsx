"use client";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { usePaymentsChannels } from "@/lib/useBillingCopy";
import { recordPipInstallIntent } from "@/lib/funnel";

const mainSteps = [
  {
    cmd: MARKET_STATS.pipInstallCmd,
    out_es: "Desde $9/mes · Starter, Pro $49, Enterprise custom",
    out_en: "From $9/mo · Starter, Pro $49, Enterprise custom",
    label: "Install",
    icon: "↓",
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
];

const devSteps = [
  { cmd: "market init", label: "Init" },
  { cmd: "market discover --country PE", label: "Discover" },
  { cmd: "market mcp-setup --ide cursor", label: "IDE setup" },
  { cmd: "market tools", label: `${MARKET_STATS.mcpTools} tools` },
];

export default function HowItWorks() {
  const { lang } = useLang();
  const isES = lang === "es";
  const paymentsLabel = usePaymentsChannels(isES);

  return (
    <section id="how-it-works" className="brand-mode-terminal landing-section landing-section-alt landing-section-glow animate-fade-in">
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4 mt-2">
            {isES ? "Cómo funciona" : "How it works"}
          </p>
          <h2 className="section-title">
            {isES ? "Tres pasos hasta precios comparables." : "Three steps to comparable prices."}
          </h2>
          <p className="section-intro">
            {isES
              ? "Instala, compara y arma canastas. Init, Discover y MCP quedan en la ruta avanzada."
              : "Install, compare, and build baskets. Init, Discover, and MCP live in the advanced path."}
          </p>
        </div>

        <div className="landing-content-rail grid grid-cols-1 sm:grid-cols-3 gap-5 text-left mb-8 min-w-0">
          {mainSteps.map((s, i) => (
            <motion.div
              key={s.label}
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
                <p className="text-sm font-bold text-gray-900">{s.label}</p>
                <p className="text-sm text-[var(--cm-on-surface-variant)] mt-1 leading-snug">{isES ? s.out_es : s.out_en}</p>
                <p className="text-[11px] text-[var(--cm-on-surface-variant)]/45 font-mono mt-2 demo-step-text">{s.cmd}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <details className="details-disclosure landing-content-narrow text-left mb-8">
          <summary>{isES ? "Ruta developer: Init · Discover · MCP setup" : "Developer path: Init · Discover · MCP setup"}</summary>
          <div className="details-body pt-4 space-y-3">
            {devSteps.map((s) => (
              <div key={s.cmd} className="card-cyber px-4 py-3 flex items-center justify-between gap-4">
                <span className="text-xs font-bold text-gray-900">{s.label}</span>
                <code className="text-xs font-mono text-[var(--cm-on-surface-variant)]">{s.cmd}</code>
              </div>
            ))}
            <p className="text-xs text-[var(--cm-on-surface-variant)]/70 font-mono">
              {isES
                ? `Bundles Shop · Intel · Account · checkout Pro vía ${paymentsLabel}`
                : `Shop · Intel · Account bundles · Pro checkout via ${paymentsLabel}`}
            </p>
          </div>
        </details>

        <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mb-6 font-mono">
          {isES ? `Checkout ${paymentsLabel} · requiere plan Pro + activación por email` : `Checkout via ${paymentsLabel} · requires Pro plan + email activation`}
        </p>

        <div className="mt-8 flex flex-wrap justify-center items-center gap-2">
          <span className="text-[11px] font-mono uppercase tracking-widest text-[var(--cm-on-surface-variant)]/40 mr-1">
            {isES ? "Compatible con" : "Works with"}
          </span>
          {["Claude", "Cursor", "GPT-4o", "LangChain", "Any HTTP"].map((tool) => (
            <span
              key={tool}
              className="text-[11px] font-mono text-[var(--cm-on-surface-variant)]/55 bg-gray-50 border border-gray-200 rounded-full px-2.5 py-0.5"
            >
              {tool}
            </span>
          ))}
        </div>

        <p className="mt-4">
          <a href="/docs#quickstart" className="font-mono text-xs underline underline-offset-2 decoration-[var(--cm-mint)]/30 text-[var(--cm-mint)]/70 hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Demo completa de 8 pasos →" : "Full 8-step walkthrough →"}
          </a>
        </p>
      </div>
    </section>
  );
}
