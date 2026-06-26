"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";

export default function ProblemSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  const cards = [
    {
      title: isES
        ? "Los datos oficiales llegan tarde"
        : "Official data arrives too late",
      body: isES
        ? "IPC y paneles tradicionales tienen semanas de retraso. Analistas y fondos necesitan señales de góndola antes de que el mercado las descuente."
        : "CPI and legacy panels lag by weeks. Analysts and funds need shelf signals before the market prices them in.",
    },
    {
      title: isES
        ? "Comprar en LATAM sigue siendo manual"
        : "Buying in LATAM is still manual",
      body: isES
        ? "Equipos de compras comparan en WhatsApp, Excel y múltiples apps. Sin trazabilidad ni precios normalizados por unidad."
        : "Procurement teams compare across WhatsApp, spreadsheets, and multiple apps. No audit trail or per-unit normalized prices.",
    },
    {
      title: isES
        ? "Los agentes IA no tienen precios reales"
        : "AI agents don't have real prices",
      body: isES
        ? "Los modelos alucinan precios o usan datos viejos. Developers necesitan una API verificada — no otro scraper que se rompe cada mes."
        : "Models hallucinate prices or use stale data. Developers need a verified API — not another scraper that breaks every month.",
    },
  ];

  return (
    <section
      ref={ref}
      id="problem"
      className="landing-section scroll-mt-24"
      style={{ backgroundColor: "#f8fafc" }}
    >
      <div className="landing-container-wide text-center">
        <motion.div
          className="landing-section-header"
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <h2 className="section-title text-[#0f172a]">
            {isES
              ? "Los precios de góndola en LATAM están fragmentados"
              : "LATAM shelf prices are fragmented"}
          </h2>
          <p className="section-intro text-[#64748b]">
            {isES
              ? "CLI Market unifica esa data en una sola capa — con tres formas de consumirla según su rol."
              : "CLI Market unifies that data in one layer — with three ways to consume it depending on your role."}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
          {cards.map((card, i) => (
            <motion.div
              key={i}
              className="card-cyber rounded-2xl p-6 text-left"
              initial={{ opacity: 0, y: 32 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.55, delay: 0.1 + i * 0.08, ease: [0.16, 1, 0.3, 1] }}
            >
              <h3 className="text-base font-semibold text-[#0f172a] mb-3">{card.title}</h3>
              <p className="text-sm leading-relaxed text-[#64748b]">{card.body}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
