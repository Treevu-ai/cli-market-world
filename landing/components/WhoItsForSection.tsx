"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { PROCURE_SITE_URL } from "@/lib/procurePlans";

export default function WhoItsForSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  const cards = [
    {
      title_es: "Developers y AI builders",
      title_en: "Developers & AI builders",
      body_es: "Agentes de compra, copilots y productos nativos para IA sobre API, MCP y SDK.",
      body_en: "Shopping agents, copilots, and AI-native products on API, MCP, and SDK.",
      features_es: ["Python SDK · CLI · REST", "MCP tools", "LangChain · Vercel AI SDK"],
      features_en: ["Python SDK · CLI · REST", "MCP tools", "LangChain · Vercel AI SDK"],
      cta_es: "Explorar Docs →",
      cta_en: "Explore Docs →",
      href: "/docs",
    },
    {
      title_es: "Equipos de compras",
      title_en: "Procurement teams",
      body_es: "Restaurantes, hoteles y operaciones que compran a escala — sin escribir código.",
      body_en: "Restaurants, hotels, and ops teams buying at scale — without writing code.",
      features_es: ["Comparar multi-retailer", "Aprobaciones y audit trail", "Checkout integrado"],
      features_en: ["Multi-retailer compare", "Approvals & audit trail", "Integrated checkout"],
      cta_es: "Ver Procure →",
      cta_en: "See Procure →",
      href: `${PROCURE_SITE_URL}/procure`,
      external: true,
    },
    {
      title_es: "Analistas y fondos",
      title_en: "Analysts & funds",
      body_es: "Pricing, trade marketing y fintech que necesitan señales de góndola antes del IPC.",
      body_en: "Pricing, trade marketing, and fintech needing shelf signals before CPI.",
      features_es: ["Inflación por categoría", "Spreads entre cadenas", "Canasta y volatilidad"],
      features_en: ["Category inflation", "Chain spreads", "Basket & volatility"],
      cta_es: "Explorar Intelligence →",
      cta_en: "Explore Intelligence →",
      href: "/#intelligence",
    },
    {
      title_es: "Startups y producto",
      title_en: "Startups & product teams",
      body_es: "Lanza features de precios o costo de vida sin construir un data moat desde cero.",
      body_en: "Ship price or cost-of-living features without building a data moat from scratch.",
      features_es: ["Free tier generoso", "Datos normalizados kg/L", "Escala a Enterprise"],
      features_en: ["Generous free tier", "kg/L normalized data", "Scale to Enterprise"],
      cta_es: "Ver planes Build →",
      cta_en: "View Build plans →",
      href: "/#pricing",
    },
  ];

  return (
    <section ref={ref} id="who-its-for" className="landing-section scroll-mt-24" style={{ backgroundColor: "#f8fafc" }}>
      <div className="landing-container-wide text-center">
        <motion.div
          className="landing-section-header"
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="section-eyebrow mb-4">{isES ? "PARA QUIÉN ES" : "WHO IT'S FOR"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES ? "Una plataforma, cuatro perfiles" : "One platform, four profiles"}
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mt-8">
          {cards.map((card, i) => (
            <motion.div
              key={i}
              className="card-cyber rounded-2xl p-6 text-left flex flex-col"
              initial={{ opacity: 0, y: 32 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.55, delay: 0.1 + i * 0.08, ease: [0.16, 1, 0.3, 1] }}
            >
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-3">
                {isES ? card.title_es : card.title_en}
              </h3>
              <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed mb-4">
                {isES ? card.body_es : card.body_en}
              </p>
              <ul className="space-y-1.5 mb-6 flex-1">
                {(isES ? card.features_es : card.features_en).map((f, j) => (
                  <li key={j} className="flex items-center gap-2 text-xs text-[var(--cm-on-surface-variant)]">
                    <span className="w-1 h-1 rounded-full bg-[var(--cm-mint)] shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              <a
                href={card.href}
                className="text-sm font-semibold text-[var(--cm-mint)] hover:underline"
                {...("external" in card && card.external
                  ? { target: "_blank", rel: "noopener noreferrer" }
                  : {})}
              >
                {isES ? card.cta_es : card.cta_en}
              </a>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
