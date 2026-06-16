"use client";

import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLiveStats } from "@/hooks/useLiveStats";

type Signal = {
  icon: string;
  labelEs: string;
  labelEn: string;
  valueEs: string;
  valueEn: string;
  accent?: boolean;
};

export default function InProductionSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { pypiChip, priceChip, retailersVerified } = useLiveStats();

  const signals: Signal[] = [
    {
      icon: "📦",
      labelEs: "Paquete PyPI",
      labelEn: "PyPI Package",
      valueEs: `${pypiChip || `${MARKET_STATS.pypiDownloads.toLocaleString()}+`} descargas`,
      valueEn: `${pypiChip || `${MARKET_STATS.pypiDownloads.toLocaleString()}+`} downloads`,
      accent: true,
    },
    {
      icon: "🔌",
      labelEs: "Endpoints MCP activos",
      labelEn: "Live MCP endpoints",
      valueEs: `${MARKET_STATS.mcpTools} herramientas · claude.ai · ChatGPT · Cursor`,
      valueEn: `${MARKET_STATS.mcpTools} tools · claude.ai · ChatGPT · Cursor`,
    },
    {
      icon: "🛒",
      labelEs: "Retailers con precios en vivo",
      labelEn: "Retailers with live prices",
      valueEs: `${retailersVerified} verificados · ${MARKET_STATS.countries} países`,
      valueEn: `${retailersVerified} verified · ${MARKET_STATS.countries} countries`,
      accent: true,
    },
    {
      icon: "📊",
      labelEs: "Precios indexados",
      labelEn: "Indexed prices",
      valueEs: `${priceChip} · refresh cada ${MARKET_STATS.pricesRefreshHours}h`,
      valueEn: `${priceChip} · refresh every ${MARKET_STATS.pricesRefreshHours}h`,
    },
    {
      icon: "☁️",
      labelEs: "Infraestructura",
      labelEn: "Infrastructure",
      valueEs: "Railway (API) · Cloudflare Pages (landing) · edge global",
      valueEn: "Railway (API) · Cloudflare Pages (landing) · global edge",
    },
    {
      icon: "⚖️",
      labelEs: "Licencia",
      labelEn: "License",
      valueEs: `MIT · v${MARKET_STATS.packageVersion} · pip install cli-market-world`,
      valueEn: `MIT · v${MARKET_STATS.packageVersion} · pip install cli-market-world`,
    },
  ];

  const integrations = [
    { name: "claude.ai", status: isES ? "Conector activo" : "Connector live" },
    { name: "ChatGPT", status: isES ? "GPT Actions live" : "GPT Actions live" },
    { name: "Cursor", status: isES ? "MCP activo" : "MCP active" },
    { name: "VS Code", status: isES ? "MCP activo" : "MCP active" },
    { name: "Railway", status: isES ? "API en producción" : "API in production" },
    { name: "PyPI", status: isES ? "Paquete publicado" : "Package published" },
  ];

  return (
    <section
      id="in-production"
      className="brand-mode-terminal landing-section animate-fade-in"
    >
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">
            {isES ? "En producción" : "In production"}
          </p>
          <h2 className="section-title">
            {isES ? "Real. Ahora mismo." : "Real. Right now."}
          </h2>
          <p className="section-intro max-w-xl mx-auto">
            {isES
              ? `No es un demo. CLI Market está en producción con ${retailersVerified} retailers activos, ${MARKET_STATS.mcpTools} herramientas MCP funcionando en claude.ai, ChatGPT y Cursor, y precios reales de góndola actualizados cada ${MARKET_STATS.pricesRefreshHours}h.`
              : `This isn't a demo. CLI Market is live with ${retailersVerified} active retailers, ${MARKET_STATS.mcpTools} MCP tools running in claude.ai, ChatGPT and Cursor, and real shelf prices refreshed every ${MARKET_STATS.pricesRefreshHours}h.`}
          </p>
        </div>

        {/* Integration badges */}
        <div className="landing-content-rail flex flex-wrap justify-center gap-3 mb-12">
          {integrations.map((intg, i) => (
            <motion.div
              key={intg.name}
              initial={{ opacity: 0, scale: 0.92 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "0px 0px -60px 0px" }}
              transition={{ duration: 0.35, delay: i * 0.06 }}
              className="flex items-center gap-2 bg-white/5 border border-[var(--cm-outline-variant)]/30 rounded-full px-4 py-2"
            >
              <span className="h-2 w-2 rounded-full bg-[var(--cm-mint)] animate-pulse flex-shrink-0" aria-hidden />
              <span className="text-xs font-bold text-white">{intg.name}</span>
              <span className="text-xs font-mono text-[var(--cm-mint)]">{intg.status}</span>
            </motion.div>
          ))}
        </div>

        {/* Signal cards */}
        <div className="landing-content-rail grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
          {signals.map((s, i) => (
            <motion.div
              key={s.labelEn}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "0px 0px -60px 0px" }}
              transition={{ duration: 0.4, delay: i * 0.07 }}
              className={`card-cyber p-5 text-left border-l-2 ${
                s.accent
                  ? "border-[var(--cm-mint)]"
                  : "border-[var(--cm-outline-variant)]/40"
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg" aria-hidden>{s.icon}</span>
                <p className="text-xs uppercase tracking-widest text-[var(--cm-on-surface-variant)]/60">
                  {isES ? s.labelEs : s.labelEn}
                </p>
              </div>
              <p className={`text-sm font-mono leading-relaxed ${
                s.accent ? "text-[var(--cm-mint)]" : "text-[var(--cm-on-surface-variant)]"
              }`}>
                {isES ? s.valueEs : s.valueEn}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Social proof line */}
        <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]/50 text-center max-w-lg mx-auto">
          {isES
            ? `Código abierto MIT · ${MARKET_STATS.pypiDownloads.toLocaleString()}+ descargas · ${MARKET_STATS.mcpTools} herramientas MCP · ${retailersVerified} retailers verificados`
            : `Open source MIT · ${MARKET_STATS.pypiDownloads.toLocaleString()}+ downloads · ${MARKET_STATS.mcpTools} MCP tools · ${retailersVerified} verified retailers`}
        </p>
      </div>
    </section>
  );
}
