"use client";

import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function AdvisorStatsStrip() {
  const { lang } = useLang();
  const isES = lang === "es";

  const stats = [
    { n: MARKET_STATS.pricesVerifiedLabel, l: isES ? "Precios verificados" : "Verified prices" },
    { n: String(MARKET_STATS.retailersVerified), l: isES ? "Retailers activos" : "Active retailers" },
    { n: String(MARKET_STATS.countries), l: isES ? "Países" : "Countries" },
    { n: String(MARKET_STATS.mcpTools), l: isES ? "Herramientas MCP" : "MCP tools" },
  ];

  return (
    <section className="landing-section landing-section-alt scroll-mt-24">
      <div className="landing-container-wide">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-40px" }}
          transition={{ duration: 0.45, ease: "easeOut" }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center max-w-[720px] mx-auto"
        >
          {stats.map((s) => (
            <div key={s.l}>
              <div className="text-3xl font-black text-[var(--cm-mint)] tabular-nums">{s.n}</div>
              <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{s.l}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
