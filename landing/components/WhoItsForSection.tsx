"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";

export default function WhoItsForSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  const cards = [
    {
      title_en: "Developers",
      title_es: "Desarrolladores",
      body_en: "Build shopping agents, copilots, and AI-native commerce products.",
      body_es: "Construye agentes de compras, copilots y productos de comercio nativos para IA.",
      features_en: ["Python SDK", "CLI", "REST API", "MCP tools"],
      features_es: ["Python SDK", "CLI", "REST API", "Herramientas MCP"],
      cta_en: "Explore Docs →",
      cta_es: "Explorar Docs →",
      href: "/docs",
    },
    {
      title_en: "AI Builders",
      title_es: "Builders de IA",
      body_en: "Connect your LLM to real commerce. Shopping agents, copilots, and autonomous procurement on verified data.",
      body_es: "Conecta tu LLM al comercio real. Agentes de compras, copilots y procurement autónomo sobre datos verificados.",
      features_en: ["LangChain / CrewAI", "Vercel AI SDK", "MCP clients", "Any LLM framework"],
      features_es: ["LangChain / CrewAI", "Vercel AI SDK", "Clientes MCP", "Cualquier framework LLM"],
      cta_en: "Explore Docs →",
      cta_es: "Explorar Docs →",
      href: "/docs",
    },
    {
      title_en: "Analysts & Funds",
      title_es: "Analistas y Fondos",
      body_en: "Track retail signals before traditional datasets update.",
      body_es: "Monitorea señales de retail antes de que los datasets tradicionales se actualicen.",
      features_en: ["historical pricing", "spread analysis", "market indicators"],
      features_es: ["historial de precios", "análisis de spreads", "indicadores de mercado"],
      cta_en: "Explore Intelligence →",
      cta_es: "Explorar Intelligence →",
      href: "/#intelligence",
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
            {isES ? "Para builders, analistas y agentes" : "For builders, analysts, and agents"}
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
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
                    <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="var(--cm-mint)" strokeWidth="2.5">
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              <a
                href={card.href}
                className="text-sm font-semibold text-[var(--cm-mint)] hover:underline"
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
